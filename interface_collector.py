import os
import csv
import sys
import netmiko
from nornir import InitNornir
import nornir.core.exceptions
from nornir.core.task import Result
from nornir_netmiko import netmiko_send_command
from nornir_netmiko import netmiko_send_config
from nornir.core.filter import F
from nornir_utils.plugins.functions import print_result
import ipdb

folder = "swu_admin_switches"

switchportlist = []
macaddresslist = []


def my_task(task):
    file1 = open(
        "C:\\Users\\lucidity\\Desktop\\"+folder+"\\"+task.host.name+"SWU_admin_switchports.txt", "a")

    file2 = open(
        "C:\\Users\\lucidity\\Desktop\\"+folder+"\\SWU_admin_switches.txt", "a")
    try:
        print("starting Interface Map on " + task.host.name)
        hresults = task.run(task=netmiko_send_command,
                            command_string='show interfaces switchport')

        file1.write("-" * 50)
        file1.write(str(hresults[0]))
        interfaces = str(hresults[0])
        interfaces1 = interfaces.splitlines()
        file1.write('\n')
        file1.write("-" * 50)
        file1.write('\n')
        file1.write("-" * 50)
        file1.flush()

        for z in interfaces1:
            try:
                switchdict = {}
                intsplit = z.split()
                file1.flush()
                if intsplit[0] == "Port:" and "Gi" in intsplit[1] and "Access" in interfaces1[interfaces1.index(z)+1]:
                    port = intsplit[1]
                    accessvlan = interfaces1[interfaces1.index(z)+3].split()
                    switchdict['Switch'] = task.host.name
                    switchdict['Port'] = port
                    switchdict['Vlan'] = accessvlan[3]
                    switchportlist.append(switchdict)
            except (IndexError):
                pass

    except (netmiko.ssh_exception.NetmikoTimeoutException):
        print("Cannot connect to this device: " + task.host.name)
        file2.write("Cannot connect to this device: " + task.host.name)
        file1.write("Nornir cant Login to " + task.host.name + "\n")
        file2.flush()
        file1.flush()
        pass
    except (netmiko.ssh_exception.NetmikoAuthenticationException):
        file2.write("Cannot connect to this device: " + task.host.name)
        file1.write("Nornir cant Login to " + task.host.name + "\n")
        file2.flush()
        file1.flush()
        pass
    except(IOError):
        print("IOError?")
        file1.write(z)
        file1.flush()
        pass
    # print(switchportlist)


def macadd(task):

    file1 = open(
        "C:\\Users\\lucidity\\Desktop\\"+folder+"\\"+task.host.name+"SWU_admin_switchports.txt", "a")

    file2 = open(
        "C:\\Users\\lucidity\\Desktop\\"+folder+"\\SWU_admin_switches.txt", "a")
    try:
        hresults1 = task.run(task=netmiko_send_command,
                             command_string='show mac address-table')
        print("Collecting mac address table info on " + task.host.name)
        file1.write("-" * 50)
        file1.write(str(hresults1[0]))
        macaddresses = str(hresults1[0])
        macaddresses1 = macaddresses.splitlines()
        file1.write('\n')
        file1.write("-" * 50)

        for k in macaddresses1:
            try:
                macdict = {}
                macsplit = k.split()
                if "Gi" in macsplit[3]:
                    port = macsplit[3]
                    mac = macsplit[1]
                    vlan = macsplit[0]
                    file1.flush()
                    macdict['Switch'] = task.host.name
                    macdict['Port'] = port
                    macdict['Vlan'] = vlan
                    macdict['Mac Address'] = mac
                    macaddresslist.append(macdict)
                # ipdb.set_trace()
            except (IndexError):
                pass
        # ipdb.set_trace()
    except (netmiko.ssh_exception.NetmikoTimeoutException):
        print("Cannot connect to this device: " + task.host.name)
        file2.write("Cannot connect to this device: " + task.host.name)
        file1.write("Nornir cant Login to " + task.host.name + "\n")
        file2.flush()
        file1.flush()
        pass
    except (netmiko.ssh_exception.NetmikoAuthenticationException):
        file2.write("Cannot connect to this device: " + task.host.name)
        file1.write("Nornir cant Login to " + task.host.name + "\n")
        file2.flush()
        file1.flush()
        pass
    except(IOError):
        print("IOError?")
        file1.write(k)
        file1.flush()
        pass
    # task.close_connections()


def main():
    nr = InitNornir(config_file="nornir.yaml", core={"raise_on_error": True})
    cis = nr.filter(platform="dell_os6")
    print("starting the script!!! Thanks Khade")
    thisresult = cis.run(task=my_task)
    csv_columns = ['Switch', 'Port', 'Vlan']
    csv_file = "swu_switchports.csv"
    try:
        with open(csv_file, 'a') as csvfile:
            writer = csv.DictWriter(
                csvfile, fieldnames=csv_columns, lineterminator='\n')
            writer.writeheader()
            for data in switchportlist:
                writer.writerow(data)
    except IOError:
        print("I/O error")
    thatresult = cis.run(task=macadd)
    csv_mac_columns = ['Switch', 'Port', 'Vlan', 'Mac Address']
    csv1_file = "swu_mac_addresses.csv"
    try:
        with open(csv1_file, 'a') as csv1file:
            writer = csv.DictWriter(
                csv1file, fieldnames=csv_mac_columns, lineterminator='\n')
            writer.writeheader()
            for data in macaddresslist:
                writer.writerow(data)
    except IOError:
        print("I/O error")
    print("All done...Thanks for using Interface collector you can collect the info you need from the csv files that were created in the "+folder+" folder.")


main()
# if __name__ == "__main__":
#    main()
