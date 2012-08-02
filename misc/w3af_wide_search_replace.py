import os

for line in file('names-discovery.txt'):
    line = line.strip()
    old, new = line.split(',')

    svn_command = 'svn move plugins/discovery/%s.py plugins/discovery/%s.py' % (old, new)
    find_command_1 = "find . -name '*.py' | xargs sed -i s/%s/%s/g;" % (old, new)
    find_command_2 = "find . -name '*.pw3af' | xargs sed -i s/%s/%s/g;" % (old, new)
    find_command_3 = "find . -name '*.w3af' | xargs sed -i s/%s/%s/g;" % (old, new)

    commands = [svn_command,
                find_command_1,
                find_command_2,
                find_command_3,
                ]

    for command in commands:
        os.system(command)

