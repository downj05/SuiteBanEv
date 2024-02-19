# db.py
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, scoped_session
from command import Command2
from json_provider import JsonBase
import db_models
from colorama import Fore, Style
import argparse
from typing import Union, List
from time import time as timestamp


DEFAULT_DB_NAME = 'smuggler_suite'


class DatabaseProviderService:
    def __init__(self, database: 'DatabaseServer', db_name=DEFAULT_DB_NAME):
        self.engine = create_engine(f"mysql+mysqlconnector://{database.user}:{database.password}@{database.host_port}/{db_name}")
        self.session = scoped_session(sessionmaker(bind=self.engine))
        db_models.Base.metadata.create_all(self.engine)

    def execute_query(self, query):
        with self.session() as session:
            result = session.query(query)
            session.commit()
            return result

    def from_name(self, object, name:str) -> db_models.Base:
        # Execute query and return results t
        with self.session() as session:
            return session.query(object).filter_by(name=name).first()

    def add_record(self, record):
        with self.session() as session:
            session.add(record)
            session.commit()

    def delete_record(self, record):
        with self.session() as session:
            session.delete(record)
            session.commit()

    def get_record(self, model, **kwargs):
        with self.session() as session:
            return session.query(model).filter_by(**kwargs).first()

    def get_all_records(self, model):
        with self.session() as session:
            return session.query(model).all()

class LocalRemoteDatabaseServiceBase():
    """
    Base service for services that need data
    read/written on either local or remote.
    Handles the logic of seeing wheteher a remote
    database is selected, and if so, storing a
    database provider service with an included session.

    Provides database_selected() -> bool

    This class is not meant to be used directly, but
    rather as a base class for other services that
    need to interact with a database.
    """
    _database_server = None
    db = None
    force_local = False # For testing purposes

    def database_selected(self) -> bool:
        """
        Check if a database is selected by user
        Will use JSON database by default
        """
        if self.force_local:
            print(f"{Fore.LIGHTYELLOW_EX}Forcing local database for {self.__class__.__name__}")
            return False
        selected_database = SelectedDatabaseServerService.selected()
        if selected_database is None:
            return False
        if self._database_server != selected_database:
            self._database_server = selected_database
            self.db = DatabaseProviderService(selected_database)
        return True   

class DatabaseServer(JsonBase):
    _table_name = "database_servers"
    def __init__(self, name:str, host_port:str, user:str=None, password:str=None):
        self.name = name
        self.host_port = host_port
        self.user = user
        self.password = password

    @staticmethod
    def from_name(name:str) -> 'DatabaseServer':
        entries = DatabaseServer.all()
        print("databaseserver.from_name:",entries)
        for entry in entries:
            if entry.name == name:
                return entry
        return None


    def __repr__(self) -> str:
        return f"{self.name} | {self.host_port}"

    def __str__(self):
        return f"{Style.BRIGHT}{Fore.CYAN}{self.name}{Fore.BLACK}: {Fore.LIGHTBLUE_EX}({self.host_port}){Style.RESET_ALL}"

    def ping(self) -> int:
        """
        Test a connection to the database
        :return: True, Ping if successful, False if failed
        """
        s = timestamp()
        r = self.test_connection(self.host_port, self.user, self.password, print_info=False)
        return r, timestamp()-s
    @staticmethod
    def test_connection(host, user=None, password=None, print_info=False, db_name=DEFAULT_DB_NAME) -> 'DatabaseServer':
        """
        Test a connection to a host / host:port,
        wull prompt for credentials if required
        :param host: host or host:port
        :param db_name: database name
        :return:  DatabaseServer if successful, False if failed
        """
        def _test_engine(engine):
            session = scoped_session(sessionmaker(bind=engine))
            with session() as connection:
                result = connection.execute(text("SHOW VARIABLES LIKE 'version%'"))
                if print_info:
                    for row in result:
                        print(f"{Style.BRIGHT}{Fore.MAGENTA}{row[0]}: {Fore.GREEN}{', '.join(row[1:])}")
                    print(f"{Fore.LIGHTGREEN_EX}Connection successful!")
                return True

        # First try create a session without credentials, if the server requires it, it will prompt the user for credentials.
        # Only do this if no credentials are passed as arguments
        if user is None and password is None:
            # Create session without credentials
            engine = create_engine(f"mysql+mysqlconnector://{host}/{db_name}")
            try:
                r = _test_engine(engine)
                if r == True:
                    return DatabaseServer(None, host)
            except OperationalError as e:
                print(f"{Fore.RED}Connection failed, the server may be down:", e)
                return False

            # Credential error
            except Exception as e:
                print(f"{Fore.CYAN}Credentials likely required!:{Style.DIM}{Fore.LIGHTBLACK_EX}", e)

            user, password = input(f"{Fore.LIGHTCYAN_EX}Enter username: {Fore.LIGHTYELLOW_EX}"), input(f"{Fore.LIGHTCYAN_EX}Enter password: {Fore.LIGHTYELLOW_EX}")
        engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{db_name}")

        try:
            r = _test_engine(engine)
            if r == True:
                return DatabaseServer(None, host, user, password)

        except OperationalError as e:
            print(f"{Fore.RED}Connection failed, the server may be down:", e)
            return False
        
        except Exception as e:
            print(f"{Fore.YELLOW}Connection failed, credentials likely incorrect:", e)
            return False

class SelectedDatabaseServerService(DatabaseServer):
    """
    Store currently selected database
    """
    _table_name = "selected_database"
    
    @staticmethod
    def selected() -> Union[DatabaseServer, None]:
        """
        Fetches the selected database, if any
        :return: DatabaseServer object if selected, None if none selected
        """
        if SelectedDatabaseServerService.all() and len(SelectedDatabaseServerService.all()) > 0:
            return SelectedDatabaseServerService.all()[0]
        return None
    
    @staticmethod
    def select(value: DatabaseServer):
        """
        Sets the selected database to the given Database object
        :param value: Database object
        """

        # Delete old
        selected = SelectedDatabaseServerService.selected()
        if selected is not None:
            selected.delete()
        
        # Insert new
        selected = SelectedDatabaseServerService(value.name, value.host_port, value.user, value.password)
        selected.insert()

        
        

    @staticmethod
    def deselect():
        # Get all (should only be one)
        entries = SelectedDatabaseServerService.all()
        # If already deselected
        if len(entries) == 0:
            return
        # Delete all
        for entry in entries:
            entry.delete()

    @staticmethod
    def selected_str() -> tuple[str, bool]:
        """
        Returns a string of the selected database
        or an error message if none is selected
        The second value is a boolean indicating
        whether a database is selected or not.
        """
        selected = SelectedDatabaseServerService.selected()
        if selected is None:
            return f"{Fore.RED}No database selected! Bans will be stored locally.", False
        else:
            if DatabaseServer.test_connection(host=selected.host_port, user=selected.user, password=selected.password):
                return f"{Fore.LIGHTGREEN_EX}{selected.name} ({selected.host_port})", True
            else:
                return f"{Fore.RED}Selected database is not available! Bans will be stored locally.", False

class DatabaseCommand(Command2):
    name:str = "database"
    usage:str = """database add <name> <address:port>\t\t\t-\tadd a database, will prompt for credentials
database remove <name>\t\t\t-\tremove a database from the list
database select/deselect <name>\t\t\t-\tselect/deselect a primary database (auto connects on startup)
database list\t\t\t-\tlist all added databases
database test <name>/<address:port>\t\t\t-\ttests a databases connection, will prompt for credentials"""
    help:str = "configure ban databases, which allow sharing bans with other smuggler suite users"

    def execute(self, *cmd_args):
        """
        Usage: database/db add/remove/list/select/delect/test
        database add <name> <address:port>
        database remove <name>
        database list
        Compatible with any command that takes <address:port> as an argument"""
        parser = argparse.ArgumentParser(
            prog=DatabaseCommand.name, add_help=True, usage=DatabaseCommand.name)

        parser.add_argument('action', nargs='?', type=str, choices=['add', 'remove', 'list', 'select', 'deselect', 'test'],
                            default=None)
        args, unknown = parser.parse_known_args(cmd_args)

        if args.action is None:
            return

        if args.action == 'test':
            test_parser = argparse.ArgumentParser()
            test_parser.add_argument('address_port', type=str)
            test_args = test_parser.parse_args(unknown)
            print(f"Running database test connection for {test_args.address_port}")
            DatabaseServer.test_connection(host=test_args.address_port, print_info=True)

        elif args.action == 'add':
            add_parser = argparse.ArgumentParser()
            add_parser.add_argument('name', type=str)
            add_parser.add_argument('address_port', type=str)
            add_args = add_parser.parse_args(unknown)
            print(f"Adding database {add_args.name} at {add_args.address_port}")
            server = DatabaseServer.test_connection(host=add_args.address_port)
            # Handle failure
            if server == False:
                print(f"{Fore.RED}Database connection failed, are you using the correct address_port/credentials?{Style.RESET_ALL}")
                return
            # Ensure it is correct object
            if not isinstance(server, DatabaseServer):
                return
            
            # Add to database
            server.name = add_args.name
            server.insert()

            print(f"{Fore.LIGHTGREEN_EX}Database '{server.name}' added successfully!")
          
        elif args.action == 'remove':
            remove_parser = argparse.ArgumentParser()
            remove_parser.add_argument('name', type=str)
            remove_args = remove_parser.parse_args(unknown)
            DatabaseServer.from_name(remove_args.name).delete()
            print(f"{Fore.LIGHTYELLOW_EX}Database '{remove_args.name}' removed successfully!")

        elif args.action == 'list':
            servers = DatabaseServer.all()
            if len(servers) == 0:
                print("No servers in database")
            else:
                for server in servers:
                    print(str(server))

        elif args.action == 'select':
            select_parser = argparse.ArgumentParser()
            select_parser.add_argument('name', type=str, default=None, nargs='?')
            select_args = select_parser.parse_args(unknown)
            if select_args.name is None:
                # Show selected
                print(f"{Fore.LIGHTYELLOW_EX}Selected database: {str(SelectedDatabaseServerService.selected())}")
                return
            server = DatabaseServer.from_name(select_args.name)
            if server is None:
                print(f"{Fore.RED}Database '{select_args.name}' not found!")
                return
            SelectedDatabaseServerService.select(server)

            server = SelectedDatabaseServerService.selected()
            print(f"{Fore.LIGHTGREEN_EX}Database '{server.name}' selected successfully!")

        elif args.action == 'deselect':
            SelectedDatabaseServerService.deselect()
            print(f"{Fore.LIGHTYELLOW_EX}Database deselected successfully!")
        # try:
        #     if args[0] == "add":
        #         name = args[1]
        #         address, port = args[2].split(":")
        #         DatabaseServer(name, address, int(port)).add_to_database()
        #     elif args[0] == "remove":
        #         name = args[1]
        #         DatabaseServer.from_name(name).remove_from_database()
        #     elif args[0] == "list":
        #         servers = DatabaseServer.get_all_entries()
        #         if len(servers) == 0:
        #             print("No servers in database")
        #         else:
        #             for server in servers:
        #                 print(str(server))
        #     else:
        #         raise TypeError("Invalid argument")
        # except IndexError:
        #     raise TypeError("Invalid argument")
        # except ValueError:
        #     raise TypeError("Invalid argument")



if __name__ == '__main__':
    s1 = DatabaseProviderService(DatabaseServer.from_name("home"))
    b = db_models.Ban().get_matching_bans(s1.session, 123, "hwid1", "hwid2", "hwid3", "ip")
    print(b)