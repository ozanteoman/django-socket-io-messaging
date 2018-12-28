var http = require('http');
var server = http.createServer().listen(8002);
var io = require('socket.io').listen(server);
var cookieParser = require('cookie').parse;


io.set('authorization', function (data, callback) {

    if (!data.headers.cookie) {

        return callback('No cookie available.', false);

    } else {
        data.cookie = cookieParser(data.headers.cookie);
        data.sid = data.cookie['sessionid'];
        callback(null, true);

    }
});

//yukarıdaki kod bloğu session bilgisinin var oluğ olmadığını kontrol ediyor.


io.on('connection', function (socket) {

    socket.on('join', function (room) {
        //her kullanıcının username'i kendi oda bilgisi oluyor
        //sadece o kullanıcıya bilgi gidiyor.
        socket.join(room); //burada ilgili socketi odaya katıyoruz.
        //console.log(io.sockets.adapter.rooms)  tüm odaları gösteriyor.
    });

    socket.on('sendMessage', function (room, owner_room, owner_msg, msg) {
        //owner_msg şunu yapıyor , kullanıcı farklı pencere açmış olabilir
        //eş zamanlı olarak diğer pencelerde göndermek için tutuyor.
        socket.broadcast.to(room).emit('newMessage', owner_room, msg); //bu karşı taraftaki kullanıcı için
        //ayrıca bizim farklı ekranlarda aynı odada olma durumumuz var yani birden fazla sekmemiz olabilir.
        socket.broadcast.to(owner_room).emit('newMessage', room, owner_msg);
    })

});