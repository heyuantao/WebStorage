const proxy = require('http-proxy-middleware');
module.exports = function (app) {
    app.use(proxy("/api/**", {
        //target: "https://www.easy-mock.com/mock/5c652589d758c80490517aad/eeasnu/",
        target: "http://webstorage.heyuantao.cn/",
        changeOrigin: true,
    }));
    {/*
    app.use(proxy("/media/avatar/**", {
        //target: "https://www.easy-mock.com/mock/5c652589d758c80490517aad/eeasnu/",
        target: "http://localhost:8000/",
        changeOrigin: true,
    }));
    */}
}
