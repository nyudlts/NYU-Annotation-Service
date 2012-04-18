function Page (container, url, params) {
    'use strict';
    
    if ( !(this instanceof Page) ) {
        return new Page(container, url, params);
    }

    params = {
        url_ver: params.url_ver || 'Z39.88-2004',
		boxes: params.boxes || null,
		zoom: params.zoom || 1,
		svc_id: params.svc_id || 'info:lanl-repo/svc/getMetadata',
		layername: params.layername || 'basic',
		format: params.format || 'image/jpeg',
		metadata: params.metadata || null,
		service: params.service || null,
		controls: params.controls || [
          new OpenLayers.Control.KeyboardDefaults(),
          new OpenLayers.Control.TouchNavigation(),
          new OpenLayers.Control.ZoomPanel(),
          new OpenLayers.Control.Attribution(),
          new OpenLayers.Control.TouchNavigation({
            dragPanOptions: {
              enableKinetic: true
            }
          }),
          new OpenLayers.Control.Navigation({
            dragPanOptions: {
              enableKinetic: true
            }
          }),
          new OpenLayers.Control.ZoomPanel()
        ]            
    };
    
    var OUlayer = new OpenLayers.Layer.OpenURL('OpenURL', params.service, { layername: params.layername, format: params.format, rft_id: url, metadataUrl: params.metadata });

    if ( params.boxes ) {
      var boxes  = new OpenLayers.Layer.Vector( "Boxes" ),  // var boxes  = new OpenLayers.Layer.Boxes( "Boxes" ),
          l =  params.boxes.length;
      while (l--) {
        var ext = params.boxes[l],
            bounds = OpenLayers.Bounds.fromArray(ext, false);
        
        var box = new OpenLayers.Feature.Vector( 
                bounds.toGeometry(), 
                {coords: bounds.toString()}
        );
        
            // box.events.register("click", box, function (e) {
            //  alert('Here' ); // this.setBorder("yellow");
            // });
        
        boxes.addFeatures( box );  // boxes.addMarker( new OpenLayers.Marker.Box(bounds) );
      }
    }
    
    var metadata = OUlayer.getImageMetadata();
    var lon = metadata.width / 2;
    var lat = metadata.height / 2;
    var options = {
            center: new OpenLayers.LonLat(lon, lat),
            zoom: params.zoom,
            layers: [ OUlayer ],
            theme: params.theme || null,
            resolutions: OUlayer.getResolutions(),
            maxExtent: new OpenLayers.Bounds(0, 0, metadata.width, metadata.height),
            tileSize: OUlayer.getTileSize(),
            controls: params.controls
    };
    
    if ( boxes ) {
      options.layers.push(boxes);
    }
    
    var page = new OpenLayers.Map(container, options);
        page.pan(0, (((page.getSize().h - (page.getTileSize().h * page.resolutions[(page.resolutions.length - (page.getZoom() + 1))])) / 2) - 5));
        
    /*
     * Let the user turn on/off layers
     */
        
    page.addControl(new OpenLayers.Control.LayerSwitcher());
    
    /*
     * Let the user turn on/off layers
     */    
    
    // http://openlayers.org/dev/examples/select-feature-multilayer.html
     /*
     var sf = new OpenLayers.Control.SelectFeature(boxes);
         
     sf.events.register("featurehighlighted", function (e) {
       alert('Here' ); // this.setBorder("yellow");
     });         
         
     page.addControl(sf);
         
     sf.activate();        
    */
     var reg = /.*\/(.*)_(\d+)\..*$/;
     var res = reg.exec(page.layers[0].rft_id);
     var bookName = res[1];
     var pageNum = res[2];
     page.targetURI = 'http://dlib.nyu.edu/awdl/books/'+bookName+'/'+parseInt(pageNum, 10);//+'/?coordinates='+$("input#coord").attr('value');
   
    return page;
}
