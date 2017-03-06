#!/bin/bash

# This file is part of mc2TeX, the mathcad to TeX converter.
#
# Copyright (c) 2016 Turysaz [turysaz@posteo.org]
#
# This program is free software. You can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License version 2 for more details.
#
# You should have received a copy of the GNU General Public
# version 2 along with this program. If not, visit 
# https://www.gnu.org/licenses/ or write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.


# == INIT ==
echo "=== INIT ==="
#delete older release and create new
rm -r release
mkdir release
cd release

# == SOURCE ==
echo "=== COPY TO SRC ==="
mkdir src
cp ../__main__.py src/
cp ../mc2tex.py src/
cp ../make_build.sh src/
cp ../LICENSE src/LICENSE.txt
cp ../easygui_license.txt src/
cp -r ../easygui src/

#rm bin
echo "=== REMOVE .PYC ==="
cd src
find -name "*.pyc" -exec rm {} +

#zip
echo "=== ZIPPING SRC ==="
7z a source.zip
cd ..

#remove unzipped
echo "=== RM UNZIPPED ==="
mv src/source.zip ./
rm -r src


# == BUILD ==
echo "=== CREATE BUILD FOLDER ==="
#create build folder
mkdir build
cp ../__main__.py build/
cp ../mc2tex.py build/
cp -r ../easygui build/

#compile
echo "=== COMPILE ==="
python -m compileall build

#rm src
echo "=== RM SRC FILES FROM BUILD ==="
cd build
find -name "*.py" -exec rm {} +

# zip 
echo "=== FINISH BUILD ==="
7z a o.zip

# create executable .py file and remove container
echo '#!/usr/bin/python' | cat - o.zip > mc2TeX.py
chmod +x mc2TeX.py
rm o.zip

# move back to release dir
cd ..
mv build/mc2TeX.py ./

#remove unzipped
echo "=== RM UNZIPPED BUILD ==="
rm -r build

cp ../LICENSE ./LICENSE.txt
cp ../easygui_license.txt ./
#cp ../README ./README.txt

echo "=== CREATE SHIPPING PACKAGE ==="
7z a mc2tex.zip

