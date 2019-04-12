import React, {Component} from 'react';
import {Tabs, Table, Select, message, Modal, Button } from 'antd';
import "./index.less";
import ajaxSub from "Utils/ajax";

const TabPane = Tabs.TabPane;
const Option = Select.Option;

class VmManger extends Component {
    constructor(props) {
        super(props);
        this.state = {
            vmList: [],
            edit:false,
            branchList1:[],
            branchList2:[],
            branchList3:[],
            branchId1:null,
            branchId2:null,
            branchId3:null,
            add:false
        };
    }
    componentDidMount() {
        this.getVmList();
    }
    /**
     * 获取虚拟机列表
     */
    getVmList() {
        ajaxSub("/api?action=list_vms&last_id=0", "GET").then(ret => {
            this.setState({vmList: ret.vms});
        });
    }
    edit(){
        this.setState({
            edit:!this.state.edit
        });
        ajaxSub("/api?action=list_branches", "GET").then(ret => {
            ret.branches&&ret.branches.map((item)=>{
                item&&item.map((inItem,i)=>{
                    if(i==0){
                        if(inItem.project==1){
                            this.setState({
                                branchList1:item
                            });
                        }
                        if(inItem.project==2){
                            this.setState({
                                branchList2:item
                            });
                        }
                        if(inItem.project==3){
                            this.setState({
                                branchList3:item
                            });
                        }
                    }
                });
            });
        });
    }
    save(record){
        const {branchId1,branchId2,branchId3} = this.state;
        let query = {
            action:"modify_vm",
            vm_id:record.id,
        };
        if(branchId1){
            query.backend_id = branchId1;
        }
        if(branchId2){
            query.web_old_id = branchId2;
        }
        if(branchId3){
            query.web_new_id = branchId3;
        }
        ajaxSub("/api", "GET",query).then(ret => {
            this.getVmList();
            message.success("修改成功");
            this.setState({
                edit:false
            });
        });
    }
    updata(record){
        let query = {
            action:"upgrade",
            vm_id:record.id,
        };
        ajaxSub("/api", "GET",query).then(ret => {
            message.success("升级成功");
            this.getVmList();
        });
    }
    delete(record){
        Modal.confirm({
            title: '确认删除该虚拟机吗',
            okText: '确认',
            cancelText: '取消',
            onOk:()=>{
                let query = {
                    action:"delete_vm",
                    vm_id:record.id,
                };
                ajaxSub("/api", "GET",query).then(ret => {
                    message.success("删除成功");
                    this.getVmList();
                });
            }
        });
        
    }
    addVm(){
        this.setState({
            add:!this.state.add
        });
    }
    updataBranch(){
        ajaxSub("/api?action=update_branch", "GET").then(ret => {
            this.getVmList();
            message.success("更新成功");
        });
    }
    addVmSure(){
        let query = {
            action:"add_vm"
        };
        if(this.refs.vmIp.value){
            query.ip = this.refs.vmIp.value;
        }
        if(this.refs.vmPass.value){
            query.password = this.refs.vmPass.value;
        }
        if(this.refs.vmName.value){
            query.vm_name = this.refs.vmName.value;
        }
        ajaxSub("/api", "GET",query).then(ret => {
            message.success("新建成功");
            this.setState({
                add:false
            });
            this.getVmList();
        });
    }
    log(){
        ajaxSub("/api?action=log", "GET").then(ret => {
            Modal.info({
                title: 'log',
                width:"100%",
                content: (
                    <div dangerouslySetInnerHTML={{__html:ret}}>
                    </div>
                ),
                onOk() {},
            });
        });
        
    }
    selectBranch(from,value){
        switch(from){
        case "branch1":
            this.setState({
                branchId1:value
            });
            return;
        case "branch2":
            this.setState({
                branchId2:value
            });
            return;
        case "branch3":
            this.setState({
                branchId3:value
            });
            return;
        }
    }
    changeIn(type){
        switch(type){
        case "name":
            if(this.refs.vmName.value&&this.refs.vmName.value.length>0){
                this.refs.vmIp.disabled = "disabled";
                this.refs.vmPass.disabled = "disabled";
            }else{
                this.refs.vmIp.disabled = false;
                this.refs.vmPass.disabled = false;
            }
           
            return false;
        case "ip":
            if((this.refs.vmIp.value&&this.refs.vmIp.value.length>0)||this.refs.vmPass.value&&this.refs.vmPass.value.length>0){
                this.refs.vmName.disabled = "disabled";
            }else{
                this.refs.vmName.disabled = false;
            }
            return false;
        }
    }
    goNewPage(){
        window.open('http://192.168.1.249:9999/help', '_blank');
    }
    render() {
        const {vmList,edit,branchList1, branchList2, branchList3, add} = this.state;
        const columns = [
            {
                title: '虚拟机',
                dataIndex: 'name',
                key: 'name'
            }, {
                title: '使用状态',
                dataIndex: 'status',
                key: 'status'
            }, {
                title: '连接状态',
                dataIndex: 'conn',
                key: 'conn'
            }, {
                title: '失败描述',
                dataIndex: 'content',
                key: 'content'
            }, {
                title: '后端分支',
                key: 'branch1',
                render:(text,record)=>(
                    <span>
                        {!edit&&<span>{record.branch1}</span>}
                        {edit&&<Select style={{ width: 120 }} onChange={this.selectBranch.bind(this,"branch1")}>
                            <Option value="">请选择</Option>
                            {branchList1&&branchList1.map((item,i)=>{
                                return <Option key={i} value={item.id}>{item.name}</Option>;
                            })}
                        </Select>}
                    </span>
                )
            }, {
                title: '老web分支',
                key: 'branch2',
                render:(text,record)=>(
                    <span>
                        {!edit&&<span>{record.branch2}</span>}
                        {edit&&<Select style={{ width: 120 }} onChange={this.selectBranch.bind(this,"branch2")}>
                            <Option value="">请选择</Option>
                            {branchList2&&branchList2.map((item,i)=>{
                                return <Option key={i} value={item.id}>{item.name}</Option>;
                            })}
                        </Select>}
                    </span>
                )
            }, {
                title: '新web分支',
                key: 'branch3',
                render:(text,record)=>(
                    <span>
                        {!edit&&<span>{record.branch3}</span>}
                        {edit&&<Select style={{ width: 120 }} onChange={this.selectBranch.bind(this,"branch3")}>
                            <Option value="">请选择</Option>
                            {branchList3&&branchList3.map((item,i)=>{
                                return <Option key={i} value={item.id}>{item.name}</Option>;
                            })}
                        </Select>}
                    </span>
                )
            }, {
                title: '操作',
                key: 'action',
                render: (text, record) => (
                    <span className="statusBtn">
                        {!edit&&<span onClick={this.edit.bind(this,record)}>修改</span>}
                        {edit&&<span onClick={this.save.bind(this,record)}>保存</span>}
                        {!edit&&<span onClick={this.updata.bind(this,record)}>升级</span>}
                        {!edit&&<span onClick={this.delete.bind(this,record)}>删除</span>}
                    </span>
                )
            }
        ];
        let dataSource=[];
        vmList&&vmList.map((item,i)=>{
            dataSource = [...dataSource,{
                key:i,
                id:item.vm_id,
                name:item.vm_name,
                ip:item.ip,
                status:item.status==0?"使用中":item.status==1?"正在安装":"正在升级",
                conn:item.conn==0?"连接成功":item.conn==1?"检查中":"连接失败",
                content:item.content,
                branch1:item.backend_name,
                branch2:item.web_old_name,
                branch3:item.web_new_name
            }];
        });
        return (
            <div className="vmManger">
                <div className="btnGroup">
                    <span onClick={this.addVm.bind(this)}>创建虚拟机</span>
                    <span onClick={this.updataBranch.bind(this)}>更新分支</span>
                    <span onClick={this.log.bind(this)}>log</span>
                    <span onClick={this.goNewPage.bind(this)}>APK HELP</span>
                </div>
                {add&&<div className="addBranch">
                    <div className="selectType">
                        <div>
                            <input onChange={this.changeIn.bind(this,"name")} ref="vmName" type="text" placeholder="请输入虚拟机名称" />
                        </div>
                        <div>
                            <input onChange={this.changeIn.bind(this,"ip")} ref="vmIp" type="text" placeholder="请添加已有的虚拟机ip" />
                            <input onChange={this.changeIn.bind(this,"ip")} ref="vmPass" type="password" placeholder="请添加已有的虚拟机的root密码" />
                        </div>
                    </div>
                    <Button onClick={this.addVmSure.bind(this)}>确认创建</Button>
                </div>}    
                <Tabs defaultActiveKey="1" tabPosition="left">
                    <TabPane tab="虚拟机" key="1">
                        <Table columns={columns} dataSource={dataSource} />
                    </TabPane>
                </Tabs>
            </div>
        );
    }
}

export default VmManger;