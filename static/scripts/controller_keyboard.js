/* キーボードの入力に応じた値をWebSocketを用いてRaspberryPiのWebサーバーへ入力キーに対応したデータ（命令）を送信する
 * GoogleChrome（バージョン: 73.0.3683.86（Official Build） （64 ビット））で動作確認
 * Author:Takahiro55555
 *
 * Reference source : https://www.ipentec.com/document/javascript-accept-keydown
 */

// キーが戻ったら停止命令を送信する
function keyup(){
  switch (event.keyCode) {
    case 87:
    case 83:
    case 68:
    case 65:
      socket.emit('my_event', {"x": 0.0, "y":0.0, "b":1});
      break;
    default:
      break;
  }
}

// キーが押されたらキーに対応した命令を送信する
function keydown() {
  if(event.keyCode == 87){ // w キー（前進）
    if(event.shiftKey == true){ // ダッシュ
      socket.emit('my_event', {"x": 0, "y":1, "b":0});
      return false;
    }
    socket.emit('my_event', {"x": 0.0, "y":0.5, "b":0});
    return false;
  }else if(event.keyCode == 83){  // s キー（後進）
    if(event.shiftKey == true){ // ダッシュ
      socket.emit('my_event', {"x": 0, "y":-1, "b":0});
      return false;
    }
    socket.emit('my_event', {"x": 0.0, "y":-0.5, "b":0});
    return false;
  }else if(event.keyCode == 68){ // d キー（右折）
    if(event.shiftKey == true){ // 超信地旋回
      socket.emit('my_event', {"x": 0.707, "y":0, "b":0});
      return false;
    }
    socket.emit('my_event', {"x": 0.424, "y":0.424, "b":0});
    return false;
  }else if(event.keyCode == 65){ // a キー（左折）
    if(event.shiftKey == true){ // 超信地旋回
      socket.emit('my_event', {"x": -0.707, "y":0, "b":0});
      return false;
    }
    socket.emit('my_event', {"x": -0.424, "y":0.424, "b":0});
    return false;
  }else if(event.keyCode == 32){  // space キー
    socket.emit('my_event', {"x": 0.0, "y":0.0, "b":1});
    return false;
  }else if(event.keyCode == 81){  // q キー
    socket.emit('my_event', {"x": 0.0, "y":0.0, "b":0});
    socket.emit('my_event', {"x": 0.0, "y":0.0, "b":1});
    socket.emit('disconnect_request');
    return false;
  }
}
