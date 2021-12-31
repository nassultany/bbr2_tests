from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from time import sleep


class LinuxRouter(Node):
    "A Node with IP forwarding enabled."

    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        # Enable forwarding on the router
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()


class NetworkTopo(Topo):
    "Linux Router network connecting two hosts."

    def build(self, **_opts):

        # Add hosts
        h10 = self.addHost('h10', ip='111.0.10.2/24',
                          defaultRoute='via 111.0.10.1')
        h11 = self.addHost('h11', ip='111.0.11.2/24',
                          defaultRoute='via 111.0.11.1')
        h12 = self.addHost('h12', ip='111.0.12.2/24',
                          defaultRoute='via 111.0.12.1')
        h13 = self.addHost('h13', ip='111.0.13.2/24',
                          defaultRoute='via 111.0.13.1')
    

        h20 = self.addHost('h20', ip='114.0.20.2/24',
                          defaultRoute='via 114.0.20.1')
        h21 = self.addHost('h21', ip='114.0.21.2/24',
                          defaultRoute='via 114.0.21.1')
        h22 = self.addHost('h22', ip='114.0.22.2/24',
                          defaultRoute='via 114.0.22.1')
        h23 = self.addHost('h23', ip='114.0.23.2/24',
                          defaultRoute='via 114.0.23.1')

        # routers are on different network
        r1 = self.addHost('r1', cls=LinuxRouter, ip='111.0.10.1/24')
        r2 = self.addHost('r2', cls=LinuxRouter, ip='112.0.0.1/24')
        r3 = self.addHost('r3', cls=LinuxRouter, ip='114.0.20.1/24')

        self.addLink(h10, r1, params1={'ip':'111.0.10.2/24'}, params2={'ip':'111.0.10.1/24'})
        self.addLink(h11, r1, params1={'ip':'111.0.11.2/24'}, params2={'ip':'111.0.11.1/24'})
        self.addLink(h12, r1, params1={'ip':'111.0.12.2/24'}, params2={'ip':'111.0.12.1/24'})
        self.addLink(h13, r1, params1={'ip':'111.0.13.2/24'}, params2={'ip':'111.0.13.1/24'})


        self.addLink(h20, r3, params1={'ip':'114.0.20.2/24'}, params2={'ip':'114.0.20.1/24'})
        self.addLink(h21, r3, params1={'ip':'114.0.21.2/24'}, params2={'ip':'114.0.21.1/24'})
        self.addLink(h22, r3, params1={'ip':'114.0.22.2/24'}, params2={'ip':'114.0.22.1/24'})
        self.addLink(h23, r3, params1={'ip':'114.0.23.2/24'}, params2={'ip':'114.0.23.1/24'})

        self.addLink(r2, r3, params1={
                     'ip': '112.0.0.1/24'}, params2={'ip': '112.0.0.2/24'})
        self.addLink(r1, r2, params1={
                     'ip': '121.0.0.1/24'}, params2={'ip': '121.0.0.2/24'})


def run():
    iperf_started = False
    topo = NetworkTopo()
    net = Mininet(topo=topo)

    # start up bird on hosts
    info(net['h10'].cmd(
        'cd h10/ && sudo bird -s h10.ctl -c myconf.conf -D logfile.log -P mypid'))
    info(net['h11'].cmd(
        'cd h11/ && sudo bird -s h11.ctl -c myconf.conf -D logfile.log -P mypid'))
    info(net['h12'].cmd(
        'cd h12/ && sudo bird -s h12.ctl -c myconf.conf -D logfile.log -P mypid'))
    info(net['h13'].cmd(
        'cd h13/ && sudo bird -s h13.ctl -c myconf.conf -D logfile.log -P mypid'))

    info(net['h20'].cmd(
        'cd h20/ && sudo bird -s h20.ctl -c myconf.conf -D logfile.log -P mypid'))
    info(net['h21'].cmd(
        'cd h21/ && sudo bird -s h21.ctl -c myconf.conf -D logfile.log -P mypid'))
    info(net['h22'].cmd(
        'cd h22/ && sudo bird -s h22.ctl -c myconf.conf -D logfile.log -P mypid'))
    info(net['h23'].cmd(
        'cd h23/ && sudo bird -s h23.ctl -c myconf.conf -D logfile.log -P mypid'))

    h10_protocol = "cubic"
    h11_protocol = h10_protocol
    h12_protocol = "bbr2"
    h13_protocol = h12_protocol

    # SET TCP CONGESTION CONTROL ALGORITHM FOR SENDING HOSTS
    info(net['h10'].cmd("sudo sysctl -w net.ipv4.tcp_congestion_control=" + h10_protocol))
    info(net['h11'].cmd("sudo sysctl -w net.ipv4.tcp_congestion_control=" + h11_protocol))
    info(net['h12'].cmd("sudo sysctl -w net.ipv4.tcp_congestion_control=" + h12_protocol))
    info(net['h13'].cmd("sudo sysctl -w net.ipv4.tcp_congestion_control=" + h13_protocol))

    for i in range(4):
        info(net['h1'+str(i)].cmd('sysctl -w net.ipv4.tcp_rmem="10240 87380 25000000"'))
        info(net['h1'+str(i)].cmd('sysctl -w net.ipv4.tcp_wmem="10240 87380 25000000"'))

    for i in range(4):
        info(net['h2'+str(i)].cmd('sysctl -w net.ipv4.tcp_rmem="10240 87380 25000000"'))
        info(net['h2'+str(i)].cmd('sysctl -w net.ipv4.tcp_wmem="10240 87380 25000000"'))

    # start up bird on routers
    #for i in range(1, 5):
    for i in range(1,4):
        info(net['r'+str(i)].cmd('cd r'+str(i)+'/ && sudo bird -s r' +
             str(i)+'.ctl -c myconf.conf -D logfile.log -P mypid'))

    net.start()
    #for i in range(1, 5):
    for i in range(1,4):
        info('*** Routing Table on Router ' + str(i) + ':\n')
        info(net['r'+str(i)].cmd('route'))

    # ADJUST DELAY AS YOU NEED. CAN SET TO DIFFERENT VALUES TO TEST RTT UNFAIRNESS
    info(net['h10'].cmd('tc qdisc add dev h10-eth0 root handle 1:0 netem delay 10ms'))
    info(net['h11'].cmd('tc qdisc add dev h11-eth0 root handle 1:0 netem delay 10ms'))
    info(net['h12'].cmd('tc qdisc add dev h12-eth0 root handle 1:0 netem delay 10ms'))
    info(net['h13'].cmd('tc qdisc add dev h13-eth0 root handle 1:0 netem delay 10ms'))


    info(net['r1'].cmd('tc qdisc add dev r1-eth4 root handle 1:0 netem loss 1%'))
    i = 0
    for testcase in ['10kbit','50kbit','100kbit','1mbit','2mbit','3mbit','4mbit','5mbit','6mbit','7mbit','8mbit','9mbit','10mbit','20mbit','30mbit','40mbit','50mbit','60mbit','70mbit','80mbit','90mbit','100mbit',
                     '200mbit','300mbit','400mbit','500mbit','600mbit','700mbit','800mbit','900mbit','1000mbit','2000mbit','3000mbit','4000mbit','5000mbit','6000mbit','7000mbit',
                     '8000mbit','9000mbit','10000mbit']:
        print("In testcase: " + testcase)
        i += 1

        info(net['r2'].cmd('tc qdisc add dev r2-eth0 root handle 1:0 tbf rate 1gbit limit '+testcase+' buffer '+testcase))

        # run iperf3 and store results
        info(net['h20'].cmd(
                'iperf3 -s -p 7890 --pidfile iperfpid > server_'+ h10_protocol + '_' + h11_protocol + '_' + testcase + '.log &'))
        info(net['h21'].cmd(
                'iperf3 -s -p 7891 --pidfile iperfpid > server_'+ h11_protocol + '_' + h11_protocol + '_' + testcase + '.log &'))
        info(net['h22'].cmd(
                'iperf3 -s -p 7892 --pidfile iperfpid > server_'+ h12_protocol + '_' + h11_protocol + '_' + testcase + '.log &'))
        info(net['h23'].cmd(
                'iperf3 -s -p 7893 --pidfile iperfpid > server_'+ h13_protocol + '_' + h11_protocol + '_' + testcase + '.log &'))


        # let server get up
        sleep(1)
        # CHANGE THE REDIRECTION PATH TO WHEREEVER YOU WANT TO STORE YOUR RESULTS
        info(net['h11'].cmd('iperf3 -c 114.0.21.2 -p 7891 > ../test_results/test2/cubic-bbrv2/twohosts/trial2/'+ h11_protocol + '_h11_' + str(i)+ "_" + '.log &'))
        info(net['h12'].cmd('iperf3 -c 114.0.22.2 -p 7892 > ../test_results/test2/cubic-bbrv2/twohosts/trial2/'+ h12_protocol + '_h12_' + str(i)+ "_" + '.log &'))
        info(net['h10'].cmd('iperf3 -c 114.0.20.2 -p 7890 > ../test_results/test2/cubic-bbrv2/twohosts/trial2/'+ h10_protocol + '_h10_' + str(i)+ "_" + '.log &')) 
        info(net['h13'].cmd('iperf3 -c 114.0.23.2 -p 7893 > ../test_results/test2/cubic-bbrv2/twohosts/trial2/'+ h13_protocol + '_h13_' + str(i)+ "_" + '.log'))                

        sleep(1) # allow it to finish

        # take down iperf3 server
        info(net['h20'].cmd('sudo pkill -F iperfpid'))
        info(net['h21'].cmd('sudo pkill -F iperfpid'))
        info(net['h22'].cmd('sudo pkill -F iperfpid'))
        info(net['h23'].cmd('sudo pkill -F iperfpid'))

        # take down tc qdisc
        info(net['r2'].cmd('tc qdisc del dev r2-eth0 root'))


    CLI(net)
    # close bird => use PID from pid file
    info(net['h10'].cmd('cat mypid | xargs sudo kill'))
    info(net['h11'].cmd('cat mypid | xargs sudo kill'))
    info(net['h12'].cmd('cat mypid | xargs sudo kill'))
    info(net['h13'].cmd('cat mypid | xargs sudo kill'))

    info(net['h20'].cmd('cat mypid | xargs sudo kill'))
    info(net['h21'].cmd('cat mypid | xargs sudo kill'))
    info(net['h22'].cmd('cat mypid | xargs sudo kill'))
    info(net['h23'].cmd('cat mypid | xargs sudo kill'))

    #for i in range(1, 5):
    for i in range(1,4):
        info(net['r'+str(i)].cmd('cat mypid | xargs sudo kill'))
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
