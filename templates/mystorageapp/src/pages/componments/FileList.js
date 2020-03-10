import React from "react";
import {Table, Popconfirm, message, Button, Modal} from 'antd';
import { fromJS } from "immutable";
import { connect } from "react-redux";
import axios from 'axios';
import LinkModal from "./LinkModal";

class FileList extends React.Component{

    constructor(props) {
        super(props);
        this.state={
            pagination: fromJS({ pageSize: 10}),
            filelist:[],
            linkModalVisible:false, linkModalInstanceId:0, linkModalInstanceKey:"",
        }
    }

    componentWillReceiveProps(props) {
        const oldProps = this.props
        const newProps = props;
        if(newProps.token.value ===""){
            this.setState({fileList:[]});
        }
        if (oldProps.updateCount !== newProps.updateCount) {
            this.fetchFileList(newProps.token.value);
            return;
        }
        if ( (oldProps.token.value !== newProps.token.value)&&(newProps.token.value !=="")){
            this.fetchFileList(newProps.token.value);
            return;
        }
    }

    fetchFileList = (tokenValue)=>{
        const token = tokenValue;
        axios.post("/api/file/list/",{},{headers: {'Authorization': 'Token '+token}}
        ).then((res)=>{
            this.postProcessData(res.data);
        }).catch((err)=>{
            this.setState({fileList:[]});
            message.error('Fetch Data Error !');
        })
    }

    postProcessData =(data)=>{
        const files=data.files;
        let fileList = [];
        files.map((item,index)=>{
            const itemObject = {'id':index+1,'filename':item};
            fileList.push(itemObject);
        })
        this.setState({fileList:fileList});
    }

    handleLinkClick = (id,key)=>{
        this.setState({linkModalVisible:true,linkModalInstanceId:id,linkModalInstanceKey:key});
    }

    handleDeleteTableItem = (id,key)=>{
        const token = this.props.token.value;
        axios.post("/api/file/delete/",{"key":key},{headers: {'Authorization': 'Token '+token}}
        ).then((res)=>{
            this.fetchFileList(token);
            message.success('Delete Success !');
        }).catch((err)=>{
            message.error('Delete Error !');
        })
    }

    handleLinkModalClose =()=>{
        this.setState({linkModalVisible:false,linkModalInstanceId:0});
    }


    render() {
        const columns = [
            {title:'ID',  key:'id',dataIndex: 'id',fixed:'left',width:"8%"},
            {title:'Name',key:'filename',dataIndex:'filename'},
            {title:'Download',  key:'action',fixed: 'right',width:"8%",
                render: (text, record) => (
                    <span>
                        <a onClick={(event)=>{this.handleLinkClick(record.id,record.filename)}}>URL</a>
                    </span>
                ),
            },
            {title:'Operate',  key:'action',fixed: 'right',width:"10%",
                render: (text, record) => (
                    <span>
                        <Popconfirm title="Delete?" okText="Confirm" cancelText="Cancel"
                            onConfirm={() => { this.handleDeleteTableItem(record.id,record.filename) }}>
                            <a>Delete</a>
                        </Popconfirm>
                    </span>
                ),
            },
        ];
        return (
            <div>
                <h1>File In WebStorage</h1>

                <Table columns={columns} dataSource={this.state.fileList} pagination={this.state.pagination.toJS()} rowKey="id"/>
                <LinkModal visible={this.state.linkModalVisible} instanceid={this.state.linkModalInstanceId} instancekey={this.state.linkModalInstanceKey}
                    onOK={()=>{this.handleLinkModalClose()}}></LinkModal>
            </div>

        )
    }
}

const mapStoreToProps = (store) => {
    return {
        token:store.token,
    }
}


export default connect(mapStoreToProps,null, null, {withRef: true})(FileList)
