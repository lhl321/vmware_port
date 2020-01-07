from __future__ import print_function
from pyVim.connect import SmartConnect, SmartConnectNoSSL, Disconnect
from pyVmomi import vim
import atexit
import sys
import argparse
import re
import ssl

import tkinter  as tk         
import tkinter.messagebox
root = tk.Tk()                     
root.title('Vmware Vshpere 端口添加器(索为思)')
root.geometry('800x500')


def get_obj(content, vimtype, name=None):
    '''
    列表返回,name 可以指定匹配的对象
    '''
    container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
    obj = [ view for view in container.view]
    return obj
def get_vmware():
    lb.delete(0)
    host = e_vc.get()
    user = e_vc_user.get()
    password = e_vc_pass.get()
    if host == '' or user == '' or password == '':
        result = tkinter.messagebox.showinfo(title = '警告',message='填写VC地址，账号及密码')
        return '-1'

    esxi_host = {}

    # connect this thing
    try:
        si = SmartConnectNoSSL(
                host = host,
                user = user,
                pwd = password ,
                port=443)
        # disconnect this thing
        atexit.register(Disconnect, si)
        content = si.RetrieveContent()
        esxi_obj = get_obj(content, [vim.HostSystem] )

        



        for esxi in esxi_obj:

            if esxi.name == 'localhost.localdomain':

                lb.insert(tk.END,host)

            else:

                lb.insert(tk.END,esxi.name)



        e_group['state'] = 'normal' 
        e_vs['state'] = 'normal' 
        e_vlan['state'] = 'normal' 
        e_vs.insert(0, 'vSwitch0')
        b_add_port = tk.Button(root, text='批量添加',command=main)
        b_add_port.grid(row=6)
    except Exception as e:
        result = tkinter.messagebox.showinfo(title = '警告',message=e.msg)
    
def GetVMHosts(content, regex_esxi=None):
    host_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                        [vim.HostSystem],
                                                        True)
    obj = [host for host in host_view.view]
    match_obj = []
    if regex_esxi:
        for esxi in obj:
            if re.findall(r'%s.*' % regex_esxi, esxi.name):
                match_obj.append(esxi)
        match_obj_name = [match_esxi.name for match_esxi in match_obj]
        print("Matched ESXi hosts: %s" % match_obj_name)
        host_view.Destroy()
        return match_obj
    else:
        host_view.Destroy()
        return obj


def AddHostsPortgroup(hosts, vswitchName, portgroupName, vlanId):
    for host in hosts:
        AddHostPortgroup(host, vswitchName, portgroupName, vlanId)


def AddHostPortgroup(host, vswitchName, portgroupName, vlanId):
    portgroup_spec = vim.host.PortGroup.Specification()
    portgroup_spec.vswitchName = vswitchName
    portgroup_spec.name = portgroupName
    portgroup_spec.vlanId = int(vlanId)
    network_policy = vim.host.NetworkPolicy()
    network_policy.security = vim.host.NetworkPolicy.SecurityPolicy()
    network_policy.security.allowPromiscuous = True
    network_policy.security.macChanges = False
    network_policy.security.forgedTransmits = False
    portgroup_spec.policy = network_policy

    host.configManager.networkSystem.AddPortGroup(portgroup_spec)


def main():
    host = e_vc.get()
    user = e_vc_user.get()
    passwd = e_vc_pass.get()
    esxi1_list = lb.curselection()
    sw = e_vs.get()
    portgroup = e_group.get()
    vlanid = e_vlan.get()
    esxi1 = []
    for tmp_list in esxi1_list:
        esxi1.append(str(tmp_list))
    print(str(esxi1),sw,portgroup,vlanid,)
    if  len(str(esxi1)) <= 2:
        result = tkinter.messagebox.showinfo(title = '警告',message='请选择需要添加的ESXI主机(多选)。')
        return '-1'
    if  sw=='' or portgroup=='' or vlanid=='':
        result = tkinter.messagebox.showinfo(title = '警告',message='参数错误，请按顺序检查端口，名称及VLANid。')
        return '-1'

    context = None
    if hasattr(ssl, '_create_unverified_context'):
        context = ssl._create_unverified_context()
    serviceInstance = SmartConnect(host=host,
                                    user=user,
                                    pwd=passwd,
                                    port=443,
                                    sslContext=context)
    atexit.register(Disconnect, serviceInstance)
    content = serviceInstance.RetrieveContent()
    for esxi in esxi1:
        esxi = lb.get(int(esxi))
        hosts = GetVMHosts(content, esxi)
        try:
            AddHostsPortgroup(hosts, sw, portgroup, vlanid)
        except Exception as e:
            result = tkinter.messagebox.showinfo(title = '错误',message=e.msg)
    result = tkinter.messagebox.showinfo(title = '成功',message='添加完成')

# Main section
if __name__ == "__main__":

    l_vc = tk.Label(root, text='Vc地址：')
    l_vc.grid(row=0, sticky=tk.W)
    e_vc = tk.Entry(root)
    e_vc.grid(row=0, column=1, sticky=tk.E, padx=3)
    #user
    l_vc_user = tk.Label(root, text='Vc用户名：')
    l_vc_user.grid(row=0, column=4,sticky=tk.W)
    e_vc_user = tk.Entry(root,width = 30)
    e_vc_user.insert(0,'administrator@vsphere.local')
    e_vc_user.grid(row=0, column=5, sticky=tk.E, padx=3)
    #passwd
    l_vc_pass = tk.Label(root, text='Vc密码：')
    l_vc_pass.grid(row=0, column=9,sticky=tk.W)
    e_vc_pass = tk.Entry(root)
    e_vc_pass['show'] = '*'
    e_vc_pass.insert(0, '111111111111111')
    e_vc_pass.grid(row=0, column=10, sticky=tk.E, padx=3)

    #group_name
    l_group = tk.Label(root, text='端口组名称：')
    l_group.grid(row=3,sticky=tk.W)
    e_group = tk.Entry(root,state='disabled')

    e_group.grid(row=3, column=1, sticky=tk.E, padx=3)
    #vlan_id
    l_vlan = tk.Label(root, text='Vlan id：')
    l_vlan.grid(row=3,column=4,sticky=tk.W)
    e_vlan = tk.Entry(root,state='disabled')
    e_vlan.grid(row=3, column=5, sticky=tk.E, padx=3)

    #vs
    l_vs = tk.Label(root, text='虚拟交换机：')
    l_vs.grid(row=3,column=9,sticky=tk.W)
    e_vs= tk.Entry(root,state='disabled')
    
    e_vs.grid(row=3, column=10, sticky=tk.E, padx=3)


    #取esxi_name
    #aa=get_vmware('192.168.16.200','administrator@vsphere.local','Windows1!@#')

    #GET_ESXI
    b_getesxi = tk.Button(root, text='读取ESXI列表',command=get_vmware)
    b_getesxi.grid(row=2)


    lb=tk.Listbox(root,selectmode=tk.MULTIPLE,height=20,width= 50)
    lb.grid(row=2,column=1,columnspan=10)
    #for item in["good","nice","handsome","very good","verynice"]:
    #    lb.insert(tk.END,item)


    root.mainloop()  