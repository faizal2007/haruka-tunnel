# haruka-tunnel
Act as proxy for home server without public ip

## setup
### Server
enable gateway port at sshd_config
```bash
GatewayPorts yes
```
restart sshd

### Private server that require public
#### setup
```bash
git clone https://github.com/faizal2007/haruka-tunnel.git
cd haruka-tunnel
cp list.tunnel-sample list.tunnel
```
###  running script
setting port, client ip and ssh address in list.tunnel file

> run tunnel
```bash
./tunnel.sh
```
> kill tunnel
```bash
./tunnel.sh kill
```

Now you can access home private server using public ip server base on port configure in list.tunnel
