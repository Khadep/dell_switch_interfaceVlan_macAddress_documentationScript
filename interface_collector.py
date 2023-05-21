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


def macadd(task):
    file1 = open(
        "C:\\Users\\lucidity\\Desktop\\"+folder+"\\"+task.host.name+"SWU_admin_switchports.txt", "a")

    file2 = open(
        "C:\\Users\\lucidity\\Desktop\\"+folder+"\\SWU_admin_switches.txt", "a")
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
        except (IndexError):
            pass


def main():
    nr = InitNornir(config_file="nornir.yaml", core={"raise_on_error": True})
    cis = nr.filter(platform="dell_os6")
    print("starting the script!!! Thanks Khade")
    try:
        thisresult = cis.run(task=my_task)
    except (nornir.core.exceptions.NornirExecutionError):
        pass
    try:
        csv_columns = ['Switch', 'Port', 'Vlan']
        csv_file = "swu_switchports.csv"
        with open(csv_file, 'a') as csvfile:
            writer = csv.DictWriter(
                csvfile, fieldnames=csv_columns, lineterminator='\n')
            writer.writeheader()
            for data in switchportlist:
                writer.writerow(data)
                # ipdb.set_trace()
    except IOError:
        print("I/O error")
    try:
        thatresult = cis.run(task=macadd)
    except (nornir.core.exceptions.NornirExecutionError):
        pass
    try:
        csv_mac_columns = ['Switch', 'Port', 'Vlan', 'Mac Address']
        csv1_file = "swu_mac_addresses.csv"
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
