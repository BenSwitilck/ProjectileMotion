var viewer = new Cesium.Viewer('cesiumContainer', {
    // sceneModePicker : false,
    // vrButton: true,
    fullscreenButton: false,
    geocoder : false,
    baseLayerPicker : false,
    imageryProvider : Cesium.createTileMapServiceImageryProvider({
        url : '/images/NaturalEarthII',
        maximumLevel: 5,
        credit : 'Imagery courtesy Natual Earth'}),
});

viewer.scene.skyBox = new Cesium.SkyBox({
    sources : {
        positiveX : '/images/TychoSkymapII.t3_08192x04096/TychoSkymapII.t3_08192x04096_80_px.jpg',
        negativeX : '/images/TychoSkymapII.t3_08192x04096/TychoSkymapII.t3_08192x04096_80_mx.jpg',
        positiveY : '/images/TychoSkymapII.t3_08192x04096/TychoSkymapII.t3_08192x04096_80_py.jpg',
        negativeY : '/images/TychoSkymapII.t3_08192x04096/TychoSkymapII.t3_08192x04096_80_my.jpg',
        positiveZ : '/images/TychoSkymapII.t3_08192x04096/TychoSkymapII.t3_08192x04096_80_pz.jpg',
        negativeZ : '/images/TychoSkymapII.t3_08192x04096/TychoSkymapII.t3_08192x04096_80_mz.jpg',
    }
});
// viewer.clock.shouldAnimate = false;
viewer.scene.globe.enableLighting = true;

var socket = io.connect('http://'.concat(location.hostname, ':', location.port), {
    remeberTransport: false,
    transports: ['websocket']
});


socket.on('connect', function() {
    socket.emit('loadMessageData', window.location.pathname);
})

socket.on('loadCesiumData', function(data) {
    data = JSON.parse(data);

    var model = {
        "show": true,
        gltf: "/images/AVMT300.gltf"
    }

    data[2].model = model;

    viewer.dataSources.add(Cesium.CzmlDataSource.load(data)).then(function(ds) {
        pth = ds.entities.getById('path');
        viewer.trackedEntity = pth;

        var gui = new dat.GUI({ autoPlace: false });
        gui.add(pth, 'show').name(pth.name);
        gui.close();
        var cesiumContainer = document.getElementById('toolbar');
        cesiumContainer.appendChild(gui.domElement);
    });

})


socket.on('loadMessageData', function(mdata) {

    mdata = JSON.parse(mdata)

    var rStack = [];

    function reverseMsg(msg) {
        var oFrom = msg.from;
        msg.from = msg.to;
        msg.to = oFrom;
        return msg;
    };

    var clock = viewer.clock;
    clock.onTick.addEventListener(function() {
        var time = Cesium.JulianDate.secondsDifference(clock.currentTime, clock.startTime);

        if (clock.multiplier > 0) {

            if (mdata.length > 0 && time >= mdata[0]["time"])
            {
                var msg = mdata.shift();
                sendMessage(svg, graph, [msg], clock.multiplier);
                rStack.push(reverseMsg(msg));
            }
        }
        else if (clock.multiplier < 0)
        {

            if (rStack.length > 0 && time <= rStack[rStack.length-1]["time"])
            {
                var msg = rStack.pop();
                sendMessage(svg, graph, [msg], Math.abs(clock.multiplier));
                mdata.unshift(reverseMsg(msg));
            }
        }
    })
    socket.emit('loadCesiumData');
});
