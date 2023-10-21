# haruka-tunnel
Act as proxy for home server without public ip

## Requirement
* VPS or Cloud Server with ipv4 public ip (root access required)

## Feature
* Forward local machine port to remote server

## Compatibility
* Only tested on debian/ubuntu

## setup
### Server
enable gateway port at sshd_config
```bash
GatewayPorts yes
```
restart sshd

### Private server that need public access
#### setup
```bash
git clone https://github.com/faizal2007/haruka-tunnel.git
cd haruka-tunnel
## update setting accordingly
cp env.example .env
## ssh password-less generate
ssh-keygen -t rsa
cat ~/.ssh/id_rsa.pub | ssh bunker.example.com -p22000 "cat >> ~/.ssh/authorized_keys"
```
###  command guide
setting port, client ip and ssh address in list.tunnel file

> run tunnel
```bash
./tunnel.sh start
```
> stop tunnel
```bash
./tunnel.sh stop
```

Now you can access home private server using public ip server base on port configured
