const path = require('path');
const { merge } = require('webpack-merge');
const common = require('./webpack.config.common.js');

module.exports = merge(common, {
  mode: 'development',
  devtool: 'eval-source-map',
  optimization: {
    chunkIds: 'named',
  },
  devServer: {
    static: {
      directory: path.resolve(__dirname, './build'),
    },
    host: 'localhost',
    port: 3000,
    open: true,
    hot: true,
    historyApiFallback: true,
  },
});
