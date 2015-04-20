<script src="http://cdn.alloyui.com/3.0.1/aui/aui-min.js"></script>
<link href="http://cdn.alloyui.com/3.0.1/aui-css/css/bootstrap.min.css" rel="stylesheet"></link>  //First load the seed and CSS files

<div id="myEditor"></div>

// Then initialize AlloyUI and load the Ace Editor module.
YUI().use(
  'aui-ace-editor',
  function(Y) {
    new Y.aceEditor(
    	{
    		boundingBox: '#myEditor'  			// new instance of Ace Editor with the newly created element
    		mode: 'javascript' 					//the mode can be set to correspond to the language being typed
    		value: <body id="content"></body> 	//The editor can also be set to load with content/code already written
    	}
    ).render();
  }
);