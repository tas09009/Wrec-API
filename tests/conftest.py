import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# To be able to import functions for testing -------
# Get the root directory of your project
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add it to sys.path to make the aws_wrec_lambda module discoverable
if root_dir not in sys.path:
    sys.path.append(root_dir)