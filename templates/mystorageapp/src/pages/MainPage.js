import React from "react";
import { Upload, Button, message } from 'antd';
import axios from 'axios';
import { UploadOutlined } from '@ant-design/icons';
import WebUploader from 'webuploader';

class MainPage extends React.Component{

    constructor(props) {
        super(props);
        this.state = {
            editable: false, mediaFileList: [], mediaUploading: false, mediaPercent: 0, mediaUrl:"",
        };

    }

    componentDidMount() {
        this._uploader = null;
    }

    componentWillUnmount() {
        if(this._uploader!==null){
            this._uploader.destroy();
        }
    }

    uploadSuccessFinished =()=>{
        this.setState({mediaUploading:false,mediaPercent: 0, mediaFileList: []});
        if(this._uploader!==null){
            this._uploader.destroy();
        }
        message.success('上传成功');
    }

    uploadErrorFinished =()=>{
        this.setState({mediaUploading:false,mediaPercent: 0});
        if(this._uploader!==null){
            this._uploader.destroy();
        }
        message.error('上传失败')
    }

    handleUploadProcess =(task_id,file)=>{
        const _this=this;
        const uploader = WebUploader.create({
            //swf: 'https://cdn.bootcss.com/webuploader/0.1.1/Uploader.swf', //swf位置，这个可能与flash有关
            server: 'http://127.0.0.1:5000/api/upload/',                        //接收每一个分片的服务器地址
            chunked: true, chunkSize: 5 * 1024 * 1024, chunkRetry: 3, threads: 1, duplicate: true,
            formData: {task_id:task_id},
        });
        {/*
        uploader.on('uploadBeforeSend', function (obj, data, headers) {
            data.task_id = "abc";
            console.log(data);
        });
        */}
        //uploader.reset();

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
            axios.post('http://127.0.0.1:5000/api/upload/success',data).then((res)=>{
                console.log('Upload success finished !')
                _this.uploadSuccessFinished();
            }).catch((err)=>{
                console.log("Upload error finished !");
                _this.uploadErrorFinished();
            })
        });

        uploader.on('uploadError', function(file) {   //上传过程中发生异常，调用该方法
            console.log('Upload error finished !');
            _this.uploadErrorFinished();
        });
        {/*
        uploader.on('uploadComplete', function(file) {//上传结束，无论文件最终是否上传成功，该方法都会被调用
            console.log('Upload complete !')
        });
        */}
        const runtimeForRuid = new WebUploader.Runtime.Runtime();
        const wuFile = new WebUploader.File(new WebUploader.Lib.File(WebUploader.guid('rt_'),file));
        uploader.addFiles(wuFile);
        this._uploader = uploader;
        uploader.upload();
    }

    handleUploadClick = () => {
        const {mediaFileList} = this.state;
        const new_file = mediaFileList[0];
        this.setState({mediaUploading:true});
        this.handleUploadProcess("abcefg",new_file);
    }

    uploadFinished =()=>{
        const uploader = this._uploader;
        uploader.reset();
        this.setState({mediaFileList:[],mediaUploading:false});
    }

    render() {
        const {mediaFileList,editable,mediaUploading,mediaPercent} = this.state;
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
                <Button type="primary" onClick={this.handleUploadClick} disabled={mediaFileList.length === 0} loading={mediaUploading} style={{ marginTop: 16 }} >
                    {mediaUploading ? 'Uploading: '+mediaPercent+"%" : 'Start Upload'}
                </Button>
                <div>
                    <Button>{this.state.mediaPercent}</Button>
                </div>

            </div>
        );
    }
}

export default MainPage