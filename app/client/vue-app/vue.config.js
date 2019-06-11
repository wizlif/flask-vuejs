const BrotliPlugin = require("brotli-webpack-plugin");
const CompressionPlugin = require("compression-webpack-plugin");
const zopfli = require("@gfx/zopfli");

const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;

let plugins = [];
let optimization = {};
if (process.env.NODE_ENV === "production") {
    const compressionTest = /\.(js|css|json|txt|html|ico|svg)(\?.*)?$/i;
    plugins = [
        new BundleAnalyzerPlugin(),
        new CompressionPlugin({
            algorithm(input, compressionOptions, callback) {
                return zopfli.gzip(input, compressionOptions, callback);
            },
            compressionOptions: {
                numiterations: 15
            },
            minRatio: 0.99,
            test: compressionTest
        }),
        new BrotliPlugin({
            test: compressionTest,
            minRatio: 0.99
        })
    ];

    optimization = {
        splitChunks: {
            chunks: 'all',
            maxInitialRequests: Infinity,
            minSize: 0,
            cacheGroups: {
                vendor: {
                    test: /[\\/]node_modules[\\/]/,
                    name(module) {
                        const packageName = module.context.match(/[\\/]node_modules[\\/](.*?)([\\/]|$)/)[1];
                        return `${packageName.replace('@', '')}`;
                    },
                }
            }
        }
    };
}


module.exports = {
    configureWebpack: {
        optimization,
        plugins
    },
    pwa: {
        name: 'Domains Registry',
        themeColor: '#4DBA87',
        msTileColor: '#000000',
        appleMobileWebAppCapable: 'yes',
        appleMobileWebAppStatusBarStyle: 'black',

        workboxPluginMode: 'InjectManifest',
        workboxOptions: {
            swSrc: 'public/service-worker.js'
        }
    }
}