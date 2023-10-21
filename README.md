# haruka-tunnel
Forward Home Server (No public ip) to Public Server

## Requirement
* VPS or Cloud Server with ipv4 public ip (root access required)

## Compatibility
* Only tested on debian/ubuntu

## setup
### Server
enable gateway port at sshd_config
```bash
GatewayPorts yes
```
restart sshd
```bash
systemctl restart sshd
```

### Private server that need public access
#### setup (require root)
```bash
git clone https://github.com/faizal2007/haruka-tunnel.git
cd haruka-tunnel
## update setting accordingly
cp env.example .env
## ssh password-less generate
ssh-keygen -t rsa
cat ~/.ssh/id_rsa.pub | ssh bunker.example.com -p22000 "cat >> ~/.ssh/authorized_keys"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
###  command guide
Configure port to forward in 
> list_port.conf

eg :
| Access Port | Forward Port |
|:------------|:-------------|
| 8443 | 443 |
| 22000| 22 |

sample :
```bash
8443:443
22000:22
```

> run tunnel
```bash
./tunnel.sh start
```
> stop tunnel
```bash
./tunnel.sh stop
```

Now you can access home private server using public ip server base on port configured
