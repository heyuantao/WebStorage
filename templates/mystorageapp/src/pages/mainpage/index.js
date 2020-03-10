import React, {useRef} from "react";
import { Layout, Menu, Breadcrumb, PageHeader, Input, Button } from 'antd';
import { Row, Col } from 'antd';
import ReactUploader from "../componments/ReactUploader";
import FileList from "../componments/FileList";
import CustomPageHeader from "../componments/CustomPageHeader";
import * as tokenActionCreator from "../commons/store/tokanActionCreator";
import {connect} from "react-redux";

const { Header, Content, Footer } = Layout;

class MainPage extends React.Component{
    constructor(props) {
        super(props);
        this.state={
            updateFileListCount:0,
        }
    }
    handleFileListRefresh = ()=>{
        const newValue = this.state.updateFileListCount+1;
        this.setState({updateFileListCount:newValue})
    }
    render() {
        return (
            <Layout className="layout">
                <Header>
                    <CustomPageHeader></CustomPageHeader>
                </Header>
                <Content style={{ padding: '0 50px',height:"900px"}}>
                    <Row type="flex" justify="space-between" align="middle">
                        <Col>
                            <Button onClick={()=>{this.handleFileListRefresh()}}>Refresh</Button>
                        </Col>
                        <Col>
                            <ReactUploader></ReactUploader>
                        </Col>
                    </Row>
                    <Row type="flex" justify="space-between" align="middle" style={{marginTop:"10px"}}>
                        <Col span={24}>
                            <FileList updateCount={this.state.updateFileListCount} token={this.props.token.value}></FileList>
                        </Col>
                    </Row>
                </Content>
                <Footer style={{ textAlign: 'center' }}>File Brower</Footer>
            </Layout>
        );
    }
}


const mapStoreToProps = (store) => {
    return {
        token:store.token,
    }
}

export default connect(mapStoreToProps,null)(MainPage)
