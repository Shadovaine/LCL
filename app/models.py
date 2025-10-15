#==============================================================
# CommandDoc = Dic[str, Any]
# STRICT_CATEGORIES
# ALLOWED_CATEGORIES
#==============================================================

#---------------------Standard Library Imports---------------------
from typing import Any, Dict

# ======================================================================================
# CATEGORY WHITELIST
# ======================================================================================
# STRICT_CATEGORIES = False
ALLOWED_CATEGORIES = [
    "File_and_Directory_Management",
    "Archive_Compression_Management", 
    "System_Administration",
    "Network_Security",
    "Process_Management",
    "Text_Processing",
    "Package_Management",
    "Hardware_Information",
    "User_Management",
    "Disk_Management",
    "Environment_Variables",
    "Job_Control",
    "Remote_Access",
    "Development_Tools",
    "Monitoring_Performance"
]

# For backwards compatibility
STRICT_CATEGORIES = ALLOWED_CATEGORIES

#-------------------------------------------------------
CommandDoc = Dict[str, Any]
