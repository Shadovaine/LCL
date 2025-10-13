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
STRICT_CATEGORIES = False
ALLOWED_CATEGORIES = {
    "Archive_Compression_Mgmt",
    "File_Directory_Mgmt",
    "Hardware_Kernel_Tools",
    "Linux_Directory_System",
    "Networking_Tools",
    "Package_Management",
    "Permission_and_Ownership",
    "Process_Management",
    "Searching_and_Filtering_Management",
    "System_Administration",
    "System_Information_and_Monitoring_Management",
    "TroubleShooting_Management",
    "User_and_Group_Management",
    "Viewing_and_Editing_Management",
    "WildCards",
}

#-------------------------------------------------------
CommandDoc = Dict[str, Any]
