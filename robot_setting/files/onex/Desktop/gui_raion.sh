#!/bin/bash
# raisin GUI from raisin_raion_ws. The preload keeps the robot window from aborting on raiway's
# joint names (built by src/raisin_raiway, tools/gui_compat).
cd "$HOME/raisin_raion_ws/install" || exit 1
LD_LIBRARY_PATH="$PWD/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" \
  LD_PRELOAD="$PWD/lib/libraiway_gui_compat.so" exec ./bin/raisin_gui
