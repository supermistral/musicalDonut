const path = require("path");
const webpack = require("webpack");


module.exports = {
    context: __dirname,
    entry: [
        './assets/js/index.js',
    ],
    output: {
        path: path.resolve('./static/bundles/'),
        filename: "[name].bundle.js",
        publicPath: 'static/bundles/',
        chunkFilename: 'static/bundles/[name].chunk.js'
    },
    module: {
        rules: [
            {
                test: /\.jsx?$/, 
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader', 
                }
            },
        ],
    },
    devServer: {
        contentBase: path.resolve('./static/bundles/'),
        hot: true,
        writeToDisk: true,
        proxy: {
            '!static/bundles/**': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true,
            },
        },
    },
    optimization: {
        minimize: false,
    },
};