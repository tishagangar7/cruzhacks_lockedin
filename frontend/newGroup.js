


document.querySelectorAll('.button1').forEach(button => {
    button.addEventListener('click', function () {
      // Remove "pressed" class from all buttons
      document.querySelectorAll('.button1').forEach(btn => btn.classList.remove('pressed'));
  
      // Add "pressed" class to the clicked button
      this.classList.add('pressed');
    });
  });

  document.addEventListener('DOMContentLoaded', function () {

    const popupOverlay = document.getElementById('popupOverlay');

    const popup = document.getElementById('popup');

    const closePopup = document.getElementById('closePopup');

    // const emailInput = document.getElementById('emailInput');

    // Function to open the popup

    function openPopup() {

        popupOverlay.style.display = 'block';

    }

    // Function to close the popup

    function closePopupFunc() {

        popupOverlay.style.display = 'none';

    }

    // Function to submit the signup form

    function submitForm() {

        // const email = emailInput.value;

        // Add your form submission logic here

        // console.log(`Email submitted: ${email}`);

        closePopupFunc(); // Close the popup after form submission

    }

    // Event listeners

    // Trigger the popup to open (you can call this function on a button click or any other event)

    openPopup();

    // Close the popup when the close button is clicked

    closePopup.addEventListener('click', closePopupFunc);



    });
    // Redirect functionality for the OK button
document.getElementById('okButton').addEventListener('click', () => {
    window.location.href = 'index.html'; // Redirect to index.html in the same tab
  });

    // You can customize and expand these functions based on your specific requirements.





 