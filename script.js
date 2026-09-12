// =====================================================
// GET USER LOCATION
// =====================================================

function getLocation() {

    if (!navigator.geolocation) {

        alert(
            "Geolocation is not supported by your browser."
        );

        return;
    }


    navigator.geolocation.getCurrentPosition(

        function(position) {

            const latitude =
                position.coords.latitude;

            const longitude =
                position.coords.longitude;


            document.getElementById("latitude").value =
                latitude.toFixed(6);

            document.getElementById("longitude").value =
                longitude.toFixed(6);


            alert(
                "Location added successfully!"
            );

        },


        function(error) {

            alert(
                "Unable to get your location. " +
                "Please enter latitude and longitude manually."
            );

        }

    );

}