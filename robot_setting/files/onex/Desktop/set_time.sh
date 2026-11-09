#!/usr/bin/env bash
# Copy this PC's clock to the robot (the robot has no internet, so its clock drifts).
set -u

HOST="raiway"   # ~/.ssh/config entry (root@192.168.12.1)
SSH_OPTS="-o ConnectTimeout=5 -o StrictHostKeyChecking=accept-new"

finish() {
  echo
  read -rp "Press Enter to close..."
  exit "$1"
}

# 1) check ssh
if ssh $SSH_OPTS "$HOST" "echo ok" >/dev/null 2>&1; then
  echo "connected"
else
  echo "not connected (is this PC on the 'raiway' Wi-Fi?)"
  finish 1
fi

# 2) set time. Send UTC epoch seconds, so the robot's timezone doesn't matter.
#    NTP must be off, or timedatectl refuses and timesyncd may overwrite the time.
EPOCH="$(date +%s)"
echo "local now:  $(date '+%Y-%m-%d %H:%M:%S %Z')"
ssh $SSH_OPTS "$HOST" "
  SUDO=''; [ \"\$(id -u)\" -ne 0 ] && SUDO='sudo'
  \$SUDO timedatectl set-ntp false 2>/dev/null
  \$SUDO date -s @$EPOCH >/dev/null
  \$SUDO hwclock -w 2>/dev/null
  echo -n 'remote now: '
  date '+%Y-%m-%d %H:%M:%S %Z'
"
RC=$?

# 3) delete old raisin logs. cd first, so rm never runs in the wrong dir.
ssh $SSH_OPTS "$HOST" "
  SUDO=''; [ \"\$(id -u)\" -ne 0 ] && SUDO='sudo'
  # raisin_raion_ws, and the deprecated raisin_network_ws if it is still there
  for d in /home/raiway/raisin_raion_ws/log/raisin_raiway /home/raiway/raisin_network_ws/log/raisin_raiway; do
    [ -d \"\$d\" ] || continue
    (cd \"\$d\" && \$SUDO rm -rf raisin_19*) && echo \"removed raisin_19* logs in \$d\"
  done
" || RC=$?
finish $RC
