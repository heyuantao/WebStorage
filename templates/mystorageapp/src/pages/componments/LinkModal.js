import React from "react";
import {Table, Popconfirm, message, Button, Modal } from 'antd';
import { fromJS } from "immutable";
import { connect } from "react-redux";
import axios from 'axios';

import {CloudDownloadOutlined} from '@ant-design/icons';

class LinkModal extends React.Component{
    constructor(props) {
        super(props);
        this.state={
            url:"",
            key:"",
        }
    }

    componentWillReceiveProps(props) {
        const oldProps = this.props
        const newProps = props;
        const token = newProps.token.value;
        const id = newProps.instanceid;
        const key = newProps.instancekey;
        if(id!==0){
            this.fetchDownloadUrl(key,token);
        }
    }

    fetchDownloadUrl = (key,tokenValue)=>{
        const token = tokenValue;
        axios.post("/api/file/url/",{"key":key},{headers: {'Authorization': 'Token '+token}}
        ).then((res)=>{
            this.setState({"url":res.data.url,"key":res.data.key})
        }).catch((err)=>{
            message.error('获取数据失败');
        })
    }

    handleOk = (e) => {
        this.props.onOK();
    };

    footerContent =()=>{
        return(
            <Button key="submit" type="primary" onClick={this.handleOk}>OK</Button>
        )

    }
    render() {
        return(
            <div>
                <Modal title="Download URL" visible={this.props.visible} closable={false}
                       footer={this.footerContent()}>
                    <p>{this.state.url}</p>

                    <a href={this.state.url} target="_blank"><CloudDownloadOutlined style={{ fontSize: 30 }} /></a>
                </Modal>
            </div>
        )

    }
}

const mapStoreToProps = (store) => {
    return {
        token:store.token,
    }
}


export default connect(mapStoreToProps,null, null, {withRef: true})(LinkModal)