import os
import sys

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault("SETTINGS_MODULE", "IntelligentPretrial.settings")

    from microserver.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)