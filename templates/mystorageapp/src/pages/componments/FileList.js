import React from "react";
import {Table, Popconfirm, message} from 'antd';
import { connect } from "react-redux";
import axios from 'axios';

class FileList extends React.Component{

    constructor(props) {
        super(props);
        this.state={
            filelist:[],
        }
    }

    componentWillReceiveProps(props) {
        let oldProps = this.props
        let newProps = props;
        console.log(oldProps);
        console.log(newProps);
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
            console.log(res);
            this.postProcessData(res.data);
        }).catch((err)=>{
            message.error('获取数据失败');
            console.log(err.data)
        })
    }

    postProcessData =(data)=>{
        const files=data.files;
        let fileList = [];
        files.map((item,index)=>{
            const itemObject = {'id':index,'filename':item};
            console.log(itemObject);
            fileList.push(itemObject);
        })
        this.setState({fileList:fileList});
    }

    render() {

        const columns = [
            {title:'ID',  key:'id',dataIndex: 'id',fixed:'left',width : '5%'},
            {title:'Name',key:'filename',dataIndex:'filename'},
            {title:'Operate',  key:'action',fixed: 'right',width : '8%',
                render: (text, record) => (
                    <span>
                        <Popconfirm title="Delete?" okText="Yes" cancelText="Cancel">
                            <a>Delete</a>
                        </Popconfirm>
                    </span>
                ),
            },
        ];
        return (
            <div>
                <h1>File In WebStorage</h1>
                <Table columns={columns} dataSource={this.state.fileList} key="abc"/>
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
