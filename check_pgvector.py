import psycopg2
import logging
import os
import platform
import subprocess

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def get_postgres_info():
    """Get PostgreSQL installation information"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            dbname='James',
            user='postgres',
            password='jcjc1749'
        )
        cur = conn.cursor()
        
        # Get PostgreSQL version
        cur.execute("SELECT version()")
        version_string = cur.fetchone()[0]
        
        # Get data directory
        cur.execute("SHOW data_directory")
        data_directory = cur.fetchone()[0]
        
        # Get extension directory
        cur.execute("SHOW extension_destdir")
        extension_dir = cur.fetchone()[0]
        if not extension_dir:
            # If extension_destdir is not set, use default location
            extension_dir = os.path.join(os.path.dirname(os.path.dirname(data_directory)), 'share', 'extension')
        
        # Get library directory
        lib_dir = os.path.join(os.path.dirname(os.path.dirname(data_directory)), 'lib')
        
        cur.close()
        conn.close()
        
        return {
            'version': version_string,
            'data_directory': data_directory,
            'extension_dir': extension_dir,
            'lib_dir': lib_dir
        }
    except Exception as e:
        logging.error(f"Error getting PostgreSQL information: {e}")
        return None

def check_pgvector():
    """Check if pgvector extension is available in PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            dbname='James',
            user='postgres',
            password='jcjc1749'
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        # Check if pgvector extension exists
        cur.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
        if cur.fetchone():
            logging.info("pgvector extension is installed and available")
            
            # Check vector version
            cur.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
            version = cur.fetchone()[0]
            logging.info(f"pgvector version: {version}")
            
            # Check if vector functions are available
            cur.execute("SELECT proname FROM pg_proc WHERE proname LIKE '%vector%' LIMIT 5")
            functions = cur.fetchall()
            logging.info(f"Found {len(functions)} vector-related functions")
            
            return True
        else:
            logging.error("pgvector extension is NOT installed")
            
            # Check if extension is available but not created
            cur.execute("SELECT * FROM pg_available_extensions WHERE name = 'vector'")
            if cur.fetchone():
                logging.info("pgvector is available but not created. You can create it with:")
                logging.info("CREATE EXTENSION vector;")
                return False
            else:
                logging.error("pgvector is not available in your PostgreSQL installation")
                
                # Get PostgreSQL info for installation instructions
                pg_info = get_postgres_info()
                if pg_info:
                    logging.info(f"PostgreSQL version: {pg_info['version']}")
                    logging.info("\nInstallation instructions for pgvector:")
                    
                    if platform.system() == "Windows":
                        logging.info("For Windows:")
                        logging.info("1. Download from: https://github.com/pgvector/pgvector/releases")
                        logging.info(f"2. Extract the files to your PostgreSQL directories:")
                        logging.info(f"   - .dll files to: {pg_info['lib_dir']}")
                        logging.info(f"   - .control and .sql files to: {pg_info['extension_dir']}")
                        logging.info("3. Restart PostgreSQL service")
                        logging.info("4. Run: CREATE EXTENSION vector;")
                    else:
                        logging.info("For Linux/macOS:")
                        logging.info("1. Install build dependencies (make, gcc, postgresql-server-dev)")
                        logging.info("2. Clone repository: git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git")
                        logging.info("3. Compile and install: cd pgvector && make && make install")
                        logging.info("4. Restart PostgreSQL service")
                        logging.info("5. Run: CREATE EXTENSION vector;")
                
                return False
            
    except Exception as e:
        logging.error(f"Error checking pgvector: {e}")
        return False
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()

def check_if_pgvector_can_be_installed():
    """Check if pgvector can be installed from the provided files in the repository"""
    try:
        # Check if we have pgvector files in the repository
        if os.path.exists("pgvector"):
            logging.info("Found pgvector directory in the repository")
            
            # Check for installation scripts
            if os.path.exists("install_pgvector.py"):
                logging.info("Found install_pgvector.py script")
                logging.info("You can run: python install_pgvector.py to install pgvector")
                return True
            
            if os.path.exists("compile_pgvector.bat") and platform.system() == "Windows":
                logging.info("Found compile_pgvector.bat script")
                logging.info("You can run: compile_pgvector.bat to compile pgvector")
                return True
                
        return False
    except Exception as e:
        logging.error(f"Error checking for pgvector installation files: {e}")
        return False

if __name__ == "__main__":
    pgvector_installed = check_pgvector()
    
    if not pgvector_installed:
        logging.info("\nChecking if pgvector can be installed from repository files...")
        can_install = check_if_pgvector_can_be_installed()
        
        if not can_install:
            logging.info("\nAlternatively, you can try running:")
            logging.info("python install_pgvector.py")
            logging.info("or")
            logging.info("compile_pgvector.bat (on Windows)")
            
            logging.info("\nAfter installation, restart PostgreSQL and run:")
            logging.info("CREATE EXTENSION vector;") 