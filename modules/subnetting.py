#!/usr/bin/env python
# encoding=utf-8
# Author: Simon Xie(Simon)
# E-mail: thimoon@sina.com
'''
Target: enable every func in http://tool.chinaz.com/Tools/subnetmask
'''
from optparse import OptionParser
import sys

addzero= lambda x : ( x not in "10" ) and '0' or x

def ip2network_address(ip, cidr):
    """
    This func also corrects wrong subnet, e.g.
    if found 10.69.231.70/29, it'll be corrected to 10.69.231.64/29.
    """
    ip = ip.split('.')
    netmask = cidr2mask(cidr)
    bin_mask_list = ip2binlist(netmask)
    for x in range(len(ip)):
        ip[x] = int(ip[x]) & int(bin_mask_list[x], 2)
    if int(cidr) < 31:
        network_address = "%s.%s.%s.%s" % (ip[0], ip[1], ip[2], ip[3])
        first_avail_ip = "%s.%s.%s.%s" % (ip[0], ip[1], ip[2], ip[3]+1)
        avail_host_numbers = 2 ** (32 - int(cidr)) - 2
        complement_bin_list = mask2complement_bin_list(netmask)
        broadcast_address = '.'.join([ str(ip[x]+int(complement_bin_list[x],2)) for x in range(4)])
        last_avail_ip_list = broadcast_address.split('.')[0:3]
        last_avail_ip_list.append( str( int(broadcast_address.split('.')[-1]) -1 ) )
        last_avail_ip = '.'.join(last_avail_ip_list)
    elif int(cidr) == 31:
        broadcast_address = network_address = None
        first_avail_ip = "%s.%s.%s.%s" % (ip[0], ip[1], ip[2], ip[3])
        last_avail_ip = "%s.%s.%s.%s" % (ip[0], ip[1], ip[2], ip[3]+1)
        avail_host_numbers = 2
    else:
        broadcast_address = network_address = None
        first_avail_ip = "%s.%s.%s.%s" % (ip[0], ip[1], ip[2], ip[3])
        last_avail_ip = first_avail_ip
        avail_host_numbers = 1
    return  avail_host_numbers, netmask, network_address, first_avail_ip,last_avail_ip, broadcast_address
def mask2cidr(mask='255.255.255.0'):
    '''
    1.  '255.11111.266.4' to '255.255.255.0' to 24
    2.  '255.128.255.0'  to 9
    '''
    mask_list = mask.split('.')
    mask_list = map(int,mask_list)                          # int list
    notexcess = lambda x: ( x > 255) and 255 or x          # if any one bigger than 255, set to 255
    # addzero= lambda x : ( x not in "10" ) and '0' or x    # set as global func
    mask_list = map(notexcess, mask_list)
    binmask_total=''
    for x in mask_list:
    #for x in range(4):
        binmask = "%8s" %bin(x).split('0b')[1]   #  '    1101'
        binmask = ''.join(map(addzero,list(binmask)))       #  '00001101'  , addzero
        binmask_total += binmask
    try:
        zindex = binmask_total.index('0')
    except ValueError:
        zindex = 32
    return  zindex

def cidr2mask(cidr='24'):
    cidr=int(cidr)
    fullnet = '0b11111111'
    zeronet = '0b00000000'
    if cidr <= 8:
        hosts = 8 - cidr
        net = '0b' + '1'* cidr + '0' * hosts
        net = (net, zeronet, zeronet, zeronet)
    elif 8 < cidr <= 16:
        hosts = 16 - cidr
        net = '0b' + '1'* (cidr-8) + '0' * hosts
        net = (fullnet, net, zeronet, zeronet)
    elif 16 < cidr <= 24:
        cidr = cidr - 16
        hosts = 8 - cidr
        net = '0b' + '1'* cidr + '0' * hosts
        net = (fullnet, fullnet, net, zeronet)
    else:
        cidr = cidr - 24
        hosts = 8 - cidr
        # print cidr,hosts
        net = '0b' + '1'* cidr + '0' * hosts
        net = (fullnet, fullnet, fullnet, net)
    netmask = '.'.join([ str(int(net[x], 2)) for x in range(len(net)) ])
    return netmask

def cidr2hex(cidr='24'):
    netmask = cidr2mask(cidr)
    bin_mask_list = ip2binlist(netmask)
    hex_list = [ hex(int(b,2)).split('0x')[1].upper() for b in bin_mask_list ]
    return hex_list


def mask2complement_bin_list(mask='255.255.255.0'):
    xcomplement_bin_list = ip2binlist(mask)
    anti = lambda x: (x == '1') and '0' or '1'
    complement_bin_list = [  ''.join(map(anti,list(x))) for x in xcomplement_bin_list ]
    return  complement_bin_list

def ipmask2network_address(ip, mask):
    cidr = mask2cidr(mask)
    return ip2network_address(ip, cidr)

def ip2binlist(ip):
    iplist = ip.split('.')
    iplist = map(int,iplist)
    binlist = []
    for x in iplist:
        binmask = "%8s" %bin(x).split('0b')[1]   #  '    1101'
        binmask = ''.join(map(addzero,list(binmask)))       #  '00001101'  , addzero
        binlist.append(binmask)
    return binlist

binlist2hexlist = lambda binlist:  [ hex(int(b,2)).split('0x')[1].upper() for b in binlist ]

def ip2hexlist(ip):
    binlist = ip2binlist(ip)
    hex_list = [ hex(int(b,2)).split('0x')[1].upper() for b in binlist ]
    return hex_list

def binlist2ip(binlist):
    add_bin_prefix = lambda binstr: '0b' + binstr
    bin2int = lambda bstr: str( int(bstr,2))
    binlist = map(add_bin_prefix,binlist)
    ip = '.'.join( map(bin2int,binlist)  )
    return ip

def hexlist2ip(hexlist):
    add_hex_prefix = lambda xstr: '0x' + xstr
    hex2int  = lambda bstr: str( int(bstr,16))
    hexlist = map(add_hex_prefix,hexlist)
    ip = '.'.join( map(hex2int,hexlist)  )
    return ip

def hexlist2binlist(hexlist):
    ip = hexlist2ip(hexlist)
    return ip2binlist(ip)


def hostamount2cidr(amount=1):
    constant_hostnumber_list = []
    for cidr in range(32,-1,-1):
        constant_hostnumber_list.append( ip2network_address(cidr=cidr)[0])
        if ip2network_address(cidr=cidr)[0] >= amount:
            return cidr

def ip2class(ip):
    '''
    A: Leading bits  0
    B: Leading bits  10
    C: Leading bits  110
    D: Leading bits  1110   (multicast)
    E: Leading bits  1111   (reserved)

    References:
    1. https://en.wikipedia.org/wiki/Classful_network#Introduction_of_address_classes
    2. http://www.tcpipguide.com/free/t_IPAddressClassABandCNetworkandHostCapacities.htm

    In the following table:
       - n indicates a bit used for the network ID.
       - H indicates a bit used for the host ID.
       - X indicates a bit without a specified purpose.

    Class A
    0.  0.  0.  0   =   00000000.00000000.00000000.00000000
    127.255.255.255 =   01111111.11111111.11111111.11111111
                        0nnnnnnn.HHHHHHHH.HHHHHHHH.HHHHHHHH
    Class B
    128.  0.  0.  0 =   10000000.00000000.00000000.00000000
    191.255.255.255 =   10111111.11111111.11111111.11111111
                        10nnnnnn.nnnnnnnn.HHHHHHHH.HHHHHHHH
    Class C
    192.  0.  0.  0 =   11000000.00000000.00000000.00000000
    223.255.255.255 =   11011111.11111111.11111111.11111111
                        110nnnnn.nnnnnnnn.nnnnnnnn.HHHHHHHH
    Class D
    224.  0.  0.  0 =   11100000.00000000.00000000.00000000
    239.255.255.255 =   11101111.11111111.11111111.11111111
                        1110XXXX.XXXXXXXX.XXXXXXXX.XXXXXXXX
    Class E
    240.  0.  0.  0 =   11110000.00000000.00000000.00000000
    255.255.255.255 =   11111111.11111111.11111111.11111111
                        1111XXXX.XXXXXXXX.XXXXXXXX.XXXXXXXX
    '''

    classful_dict = {
        int('1' * 1 + '0' * (8 - 1), 2): 'B',
        int('1' * 2 + '0' * (8 - 2), 2): 'C',
        int('1' * 3 + '0' * (8 - 3), 2): 'D',
        int('1' * 4 + '0' * (8 - 4), 2): 'E',
    }
    ip = ip2binlist(ip)[0]  # ip,  <type 'str'>
    if int(ip,2) > 255:     # typo, should be 0 <= ip <= 255
        return None
    flags=[]
    for leading in classful_dict.keys():
        if (int(ip,2) & leading) == leading:
            flags.append(leading)
    if len(flags) == 0:
        return 'A'
    return classful_dict[max(flags)]

def bin2binlist(binstr):
    raw_list = []
    result_list = []
    for x in list(binstr):
        if len(raw_list) != 7:
            raw_list.append(x)
        else:
            raw_list.append(x)
            result_list.append(''.join(raw_list))
            raw_list = []
    return  result_list

def subnetting(ip='192.168.0.1', host_amount=None, subnet_amount=None):
    default_netbits_dict = {
        'A' : 8,
        'B' : 16,
        'C' : 24,
    }

    c = ip2class(ip)
    if c not in default_netbits_dict.keys():
        print ("\nWarning, Class %s not allowed subnetting.\n" %c)
        # help_info()
    default_cidr = default_netbits_dict[c]
    default_network_address = ip2network_address(ip,default_cidr)[2]
    default_network_address_bin_list = ip2binlist(default_network_address)
    default_network_address_bin_str = ''.join(default_network_address_bin_list)
    # print default_network_address_bin_str
    # print bin2binlist(default_network_address_bin_str)
    int2binlist = lambda i:  [ bin(x).split('0b')[1].zfill(i)   for x in range(2 ** i)   ]
    '''
    In [121]: int2binlist(2)
    Out[121]: ['00', '01', '10', '11']

    In [122]: int2binlist(3)
    Out[122]: ['000', '001', '010', '011', '100', '101', '110', '111']
    '''

    if host_amount:
        host_amount = int(host_amount)
        network_address_list = []
        cidr = hostamount2cidr(host_amount)
        mask = cidr2mask(cidr)
        # print(mask)
        subnet_bits = cidr - default_cidr
        avail_host_amount = ip2network_address(ip,cidr)[0]
        if subnet_bits > 0:
            flag = 'subnet'
            subnet_amount = 2 ** subnet_bits
            sub_binlist = int2binlist(subnet_bits)
            # print sub_binlist
            for subbinstr in sub_binlist:
                fullbinstr = ''.join([ list(default_network_address_bin_str)[x] for x in range(default_cidr)]) + subbinstr + '0' * (32 - cidr)
                # print fullbinstr
                # print len(fullbinstr)
                binlist = bin2binlist(fullbinstr)
                # print binlist
                network_address_list.append( binlist2ip(binlist)  )
        else:
            flag = 'supernet'
            subnet_amount = 1
            network_address = ip2network_address(ip,cidr)[2]
            network_address_list.append(network_address)
        return cidr,c, flag,  subnet_amount,network_address_list, avail_host_amount

    elif subnet_amount:
        subnet_amount = int(subnet_amount)
        network_address_list = []
        subnet_bits = min([ subnet_bits for subnet_bits in range(32) if 2 ** subnet_bits >= subnet_amount ] )
        cidr = subnet_bits + default_cidr
        avail_host_amount = ip2network_address(ip,cidr)[0]
        if subnet_bits > 0:
            flag = 'subnet'
            sub_binlist = int2binlist(subnet_bits)
            for subbinstr in sub_binlist:
                fullbinstr = ''.join([ list(default_network_address_bin_str)[x] for x in range(default_cidr)]) + subbinstr + '0' * (32 - cidr)
                # print fullbinstr
                binlist = bin2binlist(fullbinstr)
                # print binlist
                network_address_list.append( binlist2ip(binlist)  )
        else:
            flag = 'supernet'
            subnet_amount = 1
            network_address = ip2network_address(ip,cidr)[2]
            network_address_list.append(network_address)
        return cidr,c, flag,  len(network_address_list), network_address_list, avail_host_amount
def help_info( mode='all'):
    info = ''
    print ('========================\n')
    print ('Modes Usage:')
    cut_off =  '------------------------\n'
    print (cut_off)
    info_dict = {
    1: '''Mode = 1,  Transfer IP to  the Network Address info.

    ip, mask/cidr -->
        (avail_host_numbers, netmask, network_address, first_avail_ip,last_avail_ip, broadcast_address),

    e.g.:
        --mode 1 --ip 192.168.141.111 --cidr 29
    output:
        (6, '255.255.255.248', '192.168.141.104', '192.168.141.105', '192.168.141.110','192.168.141.111')

    e.g.:
         -M 1 -i 172.16.1.1 -m 255.255.255.0
    output:
        (254, '255.255.255.0', '172.16.1.0', '172.16.1.1', '172.16.1.254', '172.16.1.255')
    ''',
    2: '''Mode = 2, Transfer cidr --> mask,

    e.g.:
        --cidr 28
    output:
        ('255.255.255.240', 'FF.FF.FF.F0')
    ''',
    3: '''Mode = 3, Transfer  mask --> cidr,

    e.g.:
        --mode 3   --mask 255.255.192.192
    output:
        ('255.255.192.0', 18)
    ''',
    4: '''Mode = 4, Subnetting for specific number of subnets that we want.

    ip, subnet_amount --> (cidr,c, flag,  subnet_amount, network_address_list, avail_host_amount)

    e.g.:
        -M 4 -i 172.16.2.33 -s 3
    output:
        (18, 'B', 'subnet', 3, ['172.16.0.0', '172.16.64.0', '172.16.128.0', '172.16.192.0'], 16382)
    ''',
    5: '''Mode = 5, Subnetting for specific number of host addresses in each subnet.

    ip, host_amount --> (cidr,c, flag,  subnet_amount,network_address_list, avail_host_amount)

    e.g.:
        -M 5 --ip 172.16.2.33 -h 9000
    output:
        (18, 'B', 'subnet', 4, ['172.16.0.0', '172.16.64.0', '172.16.128.0', '172.16.192.0'], 16382)
    ''',
    6: '''Mode = 6, Transfer ip --> (binstr, hexstr,dec),

    e.g.:
        --mode 6 --ip 192.168.141.111
    output:
        ('11000000.10101000.10001101.01101111', 'C0.A8.8D.6F', 3232271727L)
    ''',
    7: '''Mode = 7, Transfer binstr --> (ip, hexstr, dec),

    e.g.
        --mode 7 --ip 11000000.10101000.10001101.01101111
    output:
        ('192.168.141.111', 'C0.A8.8D.6F', 3232271727L)
    ''',
    8: '''Mode = 8, Transfer hexstr --> (ip, binstr, dec),

    e.g.:
        --mode 8 --ip C0.A8.8D.6F
    output:
        ('192.168.141.111', '11000000.10101000.10001101.01101111', 3232271727L)
    ''',
    9: '''Mode = 9, Transfer dec --> (ip, binstr, hexstr),

    e.g.:
        --mode 9 --ip 3232271727
    output:
        ('192.168.141.111', '11000000.10101000.10001101.01101111', 'C0.A8.8D.6F')
    ''',
    }
    try:
        print (info_dict[int(mode)])
        print (cut_off)
    except:
        for x in range(1,10):
            print (info_dict[x])
            print (cut_off)
    print ('Other modes Usage, e.g.: --mode 3 --all')
    print ('. END .')
    sys.exit(1)

def render(mode, content, detail=0):
    header_dict = {
        1: ['avail_hosts', 'netmask', 'network_address', 'first_avail_ip','last_avail_ip','broadcast_address'],
        2: ['mask','hex_mask'],
        3: ['mask','cidr'],
        4: ['cidr','class','type', 'subnet_amount', 'network_address_list', 'avail_hosts'],
        5: ['cidr','class', 'type', 'subnet_amount', 'network_address_list', 'avail_hosts'],
        6: ['binstr', 'hexstr','long_int'],
        7: ['ip', 'hexstr','long_int'],
        8: ['ip','binstr','long_int'],
        9: ['ip','binstr','hexstr'],
    }
    mode = int(mode)
    header_list = header_dict[mode]
    output = ''
    output_header = ''
    network_address_list =[]
    if mode <=3 :
        just = 20
    elif 4<= mode <= 5:
        just = 25
    else:
        just = 40

    for header in header_list:
        output_header += header.ljust(just)
    if detail>0:
        pass
    else:
        print ('=' * 35 *4 + '\n'+output_header + '\n' + '-' * 35 *4)
    for each in content:
        if type(each) is not list:
            output += str(each).ljust(just)
        else:
            network_address_list = each
            cidr = content[0]
            output += 'Details listed below'.ljust(just)
    print (output)
    if len(network_address_list) >0:
        for each_subnet in network_address_list:
            render(1,ip2network_address(each_subnet,cidr),detail)
            detail +=1

def main():

    '''
    parser blocks:
    '''

    parser = OptionParser(add_help_option=False)
    parser.add_option('-i', '--ip',
                                dest='ip', )
    parser.add_option('-c', '--cidr',
                                dest='cidr',
                                help='Specify the cidr of mask to query. e.g. --cidr 24, indicates mask=255.255.255.0')
    parser.add_option('-m', '--mask',
                                dest='mask',
                                help='Specify the Dotted Decimal mask to query. e.g. -m 255.255.0.0')
    parser.add_option('-h', '--host_amount',
                                dest='host_amount',
                                help='Specify the number of available hosts we want in each subnet.')
    parser.add_option('-s', '--subnet_amount',
                                dest='subnet_amount',
                                help='Specify the number of subnets we want.')
    parser.add_option('-M', '--mode',
                                dest='mode',
                                help='Specify  Mode 1-9 to calculate or transfer.')
    def option_without_param(option, opt_str, value, parser):
        parser.values.details = True

    parser.add_option("-a","--all", action="callback", callback=option_without_param, help='Details will be shown')
    parser.add_option('-?', '--help',
                                action='store_true',
                                help='--help --all shows Mode details.')
    (options, args) = parser.parse_args()



    ip  =   options.ip
    cidr = options.cidr
    mask = options.mask
    host_amount = options.host_amount
    subnet_amount = options.subnet_amount
    mode = options.mode

    try:
        if  options.details:
            details = options.details
    except AttributeError:
        details = None

    if options.help :
        parser.print_help()
        if details or mode:
            help_info(mode)
        parser.exit()

    if (ip or cidr or mask or host_amount or subnet_amount) is None:
        parser.print_help()
        if details or mode:
            help_info(mode)
        parser.exit()

    try:
        '''
        parameter auto-adjustment
        '''
        if cidr and (mask is None):
            mask = cidr2mask(cidr)
        if mask and (cidr is None):
            cidr = mask2cidr(mask)
        '''
        Different Modes
        '''
        if mode == '1' :
            result = ip2network_address(ip,cidr)
        elif mode == '2':
            mask = cidr2mask(cidr)
            hex = cidr2hex(cidr)
            result = (mask, '.'.join(hex))
        elif mode == '3' :
            '''
            Recall cidr2mask cuz input mask might be invalid mask,
            '''
            cidr = mask2cidr(mask)
            correct = cidr2mask(cidr)
            result = (correct, cidr)
        elif mode == '4':
            '''
            ip, subnet_amount --> (cidr,c, flag,  subnet_amount,network_address_list, avail_host_amount)
            '''
            result = subnetting(ip,subnet_amount=subnet_amount)
            # if result is None:
            #     help_info(mode)
        elif mode == '5':
            '''
            ip, host_amount --> (cidr,c, flag,  subnet_amount,network_address_list, avail_host_amount)
            '''
            result = subnetting(ip, host_amount= host_amount)
            # if result is None:
            #     help_info(mode)
        elif mode == '6':
            binstr = '.'.join(ip2binlist(ip))
            hexstr = '.'.join(ip2hexlist(ip))
            dec = int(''.join(ip2binlist(ip)),2)
            result = (binstr, hexstr,dec)
        elif mode =='7':
            binstr = ip
            binlist = binstr.split('.')
            ip = binlist2ip(binlist)
            hexstr = '.'.join(ip2hexlist(ip))
            dec = int( ''.join( binlist ) ,2)
            result = (ip, hexstr, dec)
        elif mode =='8':
            hexstr = ip
            hexlist = hexstr.split('.')
            hexlist = [  each.zfill(2) for each in hexlist  ]
            ip = hexlist2ip( hexlist )
            binstr = '.'.join(hexlist2binlist(hexlist))
            dec = int( ''.join( hexlist ) ,16)
            result = (ip, binstr, dec)
        elif mode == '9':
            dec = int(ip)
            binstr = bin(dec).split('0b')[1].zfill(32)
            binlist = bin2binlist(binstr)
            binstr = '.'.join(binlist)
            ip = binlist2ip(binlist)
            hexstr = '.'.join( binlist2hexlist(binlist) )
            result =  (ip, binstr, hexstr)
        else:
            parser.print_help()
            help_info(mode)
    except :
            help_info(mode)

    if result is None:
        help_info(mode)
    # print result
    render(mode,result)

if __name__ == '__main__':
    main()
