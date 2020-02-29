import React from "react";
import { Upload, Button, message } from 'antd';
import axios from 'axios';
import { UploadOutlined } from '@ant-design/icons';
import WebUploader from 'webuploader';
import $ from 'jquery';

class MainPage extends React.Component{

    constructor(props) {
        super(props);
        this.state = {
            editable: false, mediaFileList: [], mediaUploading: false, mediaPercent: 0, mediaUrl:"",
        };
    }

    handleUpload = () => {
        const {mediaFileList} = this.state;
        const uploader = this._uploader;
        const new_file = mediaFileList[0]
        console.log(new_file);

        uploader.reset();
        uploader.addFiles(new_file);
        console.log(uploader.getFiles());
        uploader.upload()
    }

    uploadFinished =()=>{
        const uploader = this._uploader;
        uploader.reset();
        this.setState({mediaFileList:[],mediaUploading:false});
    }

    componentDidMount() {
        const _this= this;
        const uploader = WebUploader.create({
            swf: 'https://cdn.bootcss.com/webuploader/0.1.1/Uploader.swf', //swf位置，这个可能与flash有关
            server: 'http://127.0.0.1:5000/api/upload/',                        //接收每一个分片的服务器地址
            chunked: true,                            //是否分片
            chunkSize: 5 * 1024 * 1024,              //每个分片的大小，这里为20M
            chunkRetry: 3,                            //某分片若上传失败，重试次数
            threads: 3,                               //线程数量，考虑到服务器，这里就选了1
            duplicate: true,                          //分片是否自动去重
            formData: {},
        })
        uploader.on('uploadBeforeSend', function (obj, data, headers) {
            data.task_id = "abc";
            console.log(data);
        });

        uploader.on('startUpload', function() {       //开始上传时，调用该方法
        });

        uploader.on('uploadProgress', function(file, percentage) { //一个分片上传成功后，调用该方法
            console.log(percentage);
            const percentage_string = parseInt(percentage*100);
            _this.setState({mediaPercent:percentage_string});
        });

        uploader.on('uploadSuccess', function(file) { //整个文件的所有分片都上传成功，调用该方法
            //上传的信息（文件唯一标识符，文件后缀名）
            const data = {'task_id': 'abc', 'ext': file.source['ext'], 'type': file.source['type']};
            //$.get('http://127.0.0.1:5000/api/upload/success', data);          //ajax携带data向该url发请求
            axios.post('http://127.0.0.1:5000/api/upload/success',data).then((res)=>{
                _this.uploadFinished();
            }).catch((err)=>{
                console.log("error happen");
                _this.uploadFinished();
            })
        });

        uploader.on('uploadError', function(file) {   //上传过程中发生异常，调用该方法
            console.log('upload error')
        });

        uploader.on('uploadComplete', function(file) {//上传结束，无论文件最终是否上传成功，该方法都会被调用
            console.log('upload complete')
        });
        this._uploader = uploader;

    }

    render() {
        const {mediaFileList,editable,mediaUploading} = this.state;
        const uploadButtonprops = {
            beforeUpload: file => {this.setState((state) => ({mediaFileList: [file],})); return false;},
            onChange: () =>{},
            showUploadList:false,
            mediaFileList,
        };
        return (
            <div>
                <Upload {...uploadButtonprops}>
                    <Button>
                        <UploadOutlined /> Select File
                    </Button>
                </Upload>
                <Button type="primary" onClick={this.handleUpload} disabled={mediaFileList.length === 0} loading={mediaUploading} style={{ marginTop: 16 }} >
                    {mediaUploading ? 'Uploading' : 'Start Upload'}
                </Button>
                <div>
                    <Button>{this.state.mediaPercent}</Button>
                </div>

            </div>
        );
    }
}

export default MainPage