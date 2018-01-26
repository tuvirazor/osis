function showDiv() {
    if (document.getElementById('collapse').style.display === "block") {
        document.getElementById('collapse').style.display = "none";
        document.getElementById('panel-collapse').className = "col-md-0";
        document.getElementById('panel-data').className = "col-md-12";

    } else {
        document.getElementById('collapse').style.display = "block";
        document.getElementById('panel-collapse').className = "col-md-3";
        document.getElementById('panel-data').className = "col-md-9";
    }

    document.getElementById('link_identification').href = switchUrlParameterTreeValue(document.getElementById('link_identification').href);
    document.getElementById('link_diploma').href = switchUrlParameterTreeValue(document.getElementById('link_diploma').href);
    document.getElementById('link_general_information').href = switchUrlParameterTreeValue(document.getElementById('link_general_information').href);
    document.getElementById('link_administrative').href = switchUrlParameterTreeValue(document.getElementById('link_administrative').href);
    document.getElementById('link_content').href = switchUrlParameterTreeValue(document.getElementById('link_content').href);
}

function switchUrlParameterTreeValue(currentUrlString){
    var urlObject = new URL(currentUrlString);
    var currentTreeValue = urlObject.searchParams.get("tree");
    var newTreeValue = (currentTreeValue === '0') ? '1' : '0';
    urlObject.searchParams.set("tree", newTreeValue);
    return urlObject.toString();
}


function getUrlParameterValue(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}


$(document).ready(function () {
    var $documentTree = $('#panel_file_tree');
    $documentTree.bind("loaded.jstree", function (event, data) {
        data.instance.open_all();
    });
    $documentTree.bind("changed.jstree", function (event, data) {
        document.location.href = data.node.a_attr.href;
    });
    $documentTree.jstree();

    if (getUrlParameterValue('tree') === "0") {
        showDiv();
    }
});