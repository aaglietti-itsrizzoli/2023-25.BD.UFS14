# Azure Functions

```
curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg

sudo mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg

sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/microsoft-ubuntu-$(lsb_release -cs 2>/dev/null)-prod $(lsb_release -cs 2>/dev/null) main" > /etc/apt/sources.list.d/dotnetdev.list'

sudo apt-get update

sudo apt install python3.10-venv azure-functions-core-tools-4
```

func init MyProjFolder --worker-runtime python --model V2
func new --template "Http Trigger" --name MyHttpTrigger
func new --template "Timer Trigger" --name MyTimeTrigger

func start