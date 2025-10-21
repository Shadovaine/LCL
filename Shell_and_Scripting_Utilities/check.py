# cd /home/shadovaine/GitHub/Linux-Command-Library-dev

# Check all YAML files in System Information and Monitoring Management folder
find "data/commands/System_Information_Monitoring" -name "*.yml" -exec python3 -c "
import yaml
import sys
try:
    with open('{}', 'r') as f:
        yaml.safe_load(f)
    print('✅ {}')
except Exception as e:
    print('❌ {}: {}'.format('{}', e))
" \;