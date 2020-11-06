# PACE MacOS Anvil Jenkins node setup

The PACE MacOS Anvil Jenkins node can be started by logging onto the mac mini Jenkins account and in terminal running: `cd Jenkins && ./start_agent.bash`. `start_agent.bash` is a simple bash script that kills already running agents, redownloads agent.jar for Anvil and starts up the agent with the jar.

The script is run as a cron job which restarts on Monday at 00:00 every week. You can edit this cron job by running `crontab -e` and using vim to edit the `start_agent.bash` entry. Use [crontab.guru](https://crontab.guru) to check any cron scheduling expressions. In the `crontab -e` vim you will be able to find out where logs are redirected to. When finished exit with esc and :x. You should then see the cron job has updated successfully in the output.

## Restart agent in a disowned state
`./start_agent.bash &!`

## Check if the agent is running
`pgrep -lf java`

## Notes

- Anvil uses /usr/local/bin/jenkins-sh to execute shell scripts. This is not available on our mac and is not configurable for each node. The solution was to symlink /usr/local/bin/jenkins-sh to /bin/sh
- The conda used is a Jenkins account specific conda
