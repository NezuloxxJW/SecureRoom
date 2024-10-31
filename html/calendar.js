// globals
const calendarTitle = document.getElementById('calendar-title');
const calendarDays = document.getElementById('calendar-days');
const prevMonthBtn = document.getElementById('prev-month');
const nextMonthBtn = document.getElementById('next-month');
const todayBtn = document.getElementById('today-btn');

const sidebarTitle = document.querySelector('.calendar-left h1');
const sidebarEventCount = document.querySelector('.calendar-left h3');
const sidebarEventsList = document.querySelector('.calendar-events');
const sumbitMenu = document.getElementById("submit");
const reserveMenu = document.getElementById("reservations"); 
const loginMenu = document.getElementById("login"); 

const logUserTitle = document.querySelector('.subheading');

let logged = false;
let autoLogin = true;
let selectedDate;

function logout(){
    const url = 'https://'+window.location.host+'/logout';

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include'
    })
    .then(response => response.json()).then(data => {
        if (data.status === 'success') {
            window.location.reload();
        } else {
            alert('Erreur : ' + data.message);
        }
    }).catch(error => console.error('Error:', error));
}

function showSubmitMenu()
{
    // Si pas connecter afficher seulement loginMenu
    if(logged == false){ 
        if(reserveMenu.style.display == "block"){
            loginMenu.style.display = "block"
            reserveMenu.style.display = "none"
            return
        }
        loginMenu.style.display = "none"
        reserveMenu.style.display = "block"
        return
    }

    // Quand connecter afficher le submitMenu
    if(reserveMenu.style.display == "block"){
        sumbitMenu.style.display = "block"
        reserveMenu.style.display = "none"
        return
    }

    sumbitMenu.style.display = "none"
    reserveMenu.style.display = "block"
    return
}

function deleteReservation(element) {
    const url = 'https://'+window.location.host+'/delete';
    const date = selectedDate;
    
    const reservationItem = element.closest('.reservation-item');
    const timeText = reservationItem.querySelector('.reservation-time strong').innerText;
    const firstHour = timeText.split(' -')[0];

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            date: date,
            time: firstHour,
        }),
        credentials: 'include'
    }).then(response => response.json()).then(data => {
        if (data.status === 'success') {
            sidebarEventsList.innerHTML = '';
            fetchReservations(date);
        } else {
            alert('Erreur : ' + data.message);
        }
    }).catch(error => console.error('Error:', error));
}

function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const url = 'https://'+window.location.host+'/login'
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: username,
            password: password,
        }),
		credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            logged = true;
            loginMenu.style.display = "none";
            sumbitMenu.style.display = "block";
            logUserTitle.innerText = username;
            if(autoLogin){autoLogin=false; sumbitMenu.style.display = "none"; reserveMenu.style.display = "block"; logUserTitle.innerText = data.username;}
            sidebarEventsList.innerHTML = '';
            fetchReservations(selectedDate);
        } else {
            alert('Erreur : ' + data.message);
        }
    })
    .catch(error => {fetchReservations(selectedDate); console.error('Error:', error)});
}

function convertTime(timeString) {
    // Sépare les heures et les minutes
    let [hours, minutes] = timeString.split(':').map(Number);
    
    // Vérifie si les minutes sont 60
    if (minutes === 60) {
        hours += 1; // Incrémente les heures
        minutes = 0; // Remet les minutes à 0
    }

    // Formate les heures et les minutes pour avoir toujours deux chiffres
    hours = String(hours).padStart(2, '0');
    minutes = String(minutes).padStart(2, '0');

    return `${hours}:${minutes}`;
}

function fetchReservations(date) {
    const min_hour = 7;
    const max_hour = 19;
    const url = 'https://'+window.location.host+'/get_reservations'

    fetch(url, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ date: date })
}).then(response => response.json()).then(data => {
        let reservations = data.reserved;
        sidebarEventCount.textContent = `${data.reserved.length} Réservation${data.reserved.length >= 2 ? 's' : ''}`;
        reservations.forEach(reservation => {
            const listItem = document.createElement('li');
            let html = `<div class="reservation-item">
                        <p class="reservation-time">
                        <strong>${reservation.time} -> ${convertTime(reservation.end_time)}</strong>
                        </p>`
            if (reservation.user_reservation) {
            html += `<a onclick="deleteReservation(this)" class="calendar-btn delete-btn">X</a>`
            }
            html += `<br>
                            </div>
                            <span>${reservation.description}</span>`;
            listItem.innerHTML = html;
            sidebarEventsList.appendChild(listItem);
        });
    }).catch(error => console.error('Error:', error));}


function Submit() {
    const date = selectedDate;
    const time = document.getElementById('time').value;
    const duration = document.getElementById('duration').value;
    const description = document.getElementById('description').value;

    const url = 'https://'+window.location.host+'/submit';

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            date: date,
            time: time,
            duration: duration,
            description: description
        }),
        credentials: 'include'
    }).then(response => response.json()).then(data => {
        if (data.status === 'success') {
            sidebarEventsList.innerHTML = '';
            showSubmitMenu();
            fetchReservations(date);
        } else {
            alert('Erreur : ' + data.message);
        }
    }).catch(error => console.error('Error:', error));
}

function ajouterZero(nombre) {
    if (nombre < 10) {
      return "0" + nombre;
    } else {
      return nombre.toString();
    }
  }

document.addEventListener('DOMContentLoaded', function () {
    let currentDate = new Date();
    selectedDate = formatDateString(currentDate);

    const monthNames = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Decembre'];

    // Fonction pour formater les dates en string "YYYY-MM-DD"
    function formatDateString(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    function renderEventsForDate(date) {
        const formattedDate = formatDateString(date);
        sidebarEventCount.textContent = `0 Réservation`;

        // Vider la liste d'événements actuelle
        sidebarEventsList.innerHTML = '';
        fetchReservations(formattedDate);
    }
    function renderCalendar(date) {
        const month = date.getMonth();
        const year = date.getFullYear();
        const firstDay = new Date(year, month, 1).getDay(); // Jour de la semaine du 1er du mois
        const lastDate = new Date(year, month + 1, 0).getDate(); // Dernier jour du mois actuel

        // Mettre à jour le titre du calendrier
        calendarTitle.innerHTML = `<strong>${monthNames[month]}</strong> ${year}`;

        // Effacer les jours du calendrier précédent
        calendarDays.innerHTML = '';

        // Détails du mois précédent
        const prevMonthLastDate = new Date(year, month, 0).getDate(); // Dernier jour du mois précédent

        // Calculer le premier jour à afficher (lundi comme premier jour de la semaine)
        const startDay = (firstDay === 0 ? 6 : firstDay - 1); // Ajuster pour commencer le lundi

        // Remplir les jours du mois précédent
        let row = document.createElement('div');
        row.classList.add('calendar-row');

        for (let i = startDay; i > 0; i--) {
            const prevMonthDayDiv = document.createElement('div');
            prevMonthDayDiv.classList.add('calendar-day', 'inactive');
            prevMonthDayDiv.innerHTML = `<span class="calendar-date">${prevMonthLastDate - i + 1}</span>`;
            row.appendChild(prevMonthDayDiv);
        }

        // Ajouter les jours du mois actuel
        let dayCounter = 1;
        while (dayCounter <= lastDate) {
            // Si une ligne est complète (7 jours), ajouter la ligne à la vue et en créer une nouvelle
            if (row.childElementCount === 7) {
                calendarDays.appendChild(row);
                row = document.createElement('div');
                row.classList.add('calendar-row');
            }

            const dayDiv = document.createElement('div');
            dayDiv.classList.add('calendar-day');

            // Mettre en évidence la date du jour
            if (dayCounter === currentDate.getDate() && month === currentDate.getMonth() && year === currentDate.getFullYear()) {
                dayDiv.classList.add('today');
            }

            dayDiv.innerHTML = `<span value=${dayCounter} class="calendar-date" data-date="${formatDateString(new Date(year, month, dayCounter))}">${dayCounter}</span>`;
            dayDiv.dataset.date = formatDateString(new Date(year, month, dayCounter)); // Ajouter un attribut data avec la date
            dayDiv.addEventListener('click', function () {
				let divDate = this.getAttribute('data-date').toString();
                let TempM = divDate.split("-")[1].replace(/^0/, '')

                let Y = divDate.split("-")[0]
                let D = divDate.split("-")[2].replace(/^0/, '')
                let M = parseInt(TempM)
                
                sidebarTitle.textContent = `${D} ${monthNames[M-1]}, ${Y}`;
                selectedDate = this.getAttribute('data-date').toString();
                renderEventsForDate(new Date(Y, M-1, D));
            });
            row.appendChild(dayDiv);
            dayCounter++;
        }

        // Ajouter les jours du mois suivant pour compléter la grille 7x5
        let nextMonthDayStart = 1;
        while (row.childElementCount < 7) {
            const nextMonthDayDiv = document.createElement('div');
            nextMonthDayDiv.classList.add('calendar-day', 'inactive');
            nextMonthDayDiv.innerHTML = `<span class="calendar-date">${nextMonthDayStart}</span>`;
            row.appendChild(nextMonthDayDiv);
            nextMonthDayStart++;
        }

        calendarDays.appendChild(row); // Ajouter la dernière ligne

        // Si on n'a pas assez de lignes, continuer à en ajouter jusqu'à avoir 5 lignes (35 jours)
        while (calendarDays.childElementCount < 5) {
            row = document.createElement('div');
            row.classList.add('calendar-row');
            for (let i = 0; i < 7; i++) {
                const nextMonthDayDiv = document.createElement('div');
                nextMonthDayDiv.classList.add('calendar-day', 'inactive');
                nextMonthDayDiv.innerHTML = `<span class="calendar-date">${nextMonthDayStart}</span>`;
                row.appendChild(nextMonthDayDiv);
                nextMonthDayStart++;
            }
            calendarDays.appendChild(row);
        }


    }

    // Rendu initial
    renderCalendar(currentDate);

    // Gestion de la navigation vers le mois précédent
    prevMonthBtn.addEventListener('click', (e) => {
        e.preventDefault();
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar(currentDate);
    });

    // Gestion de la navigation vers le mois suivant
    nextMonthBtn.addEventListener('click', (e) => {
        e.preventDefault();
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar(currentDate);
        
    });

    // Gestion du bouton "Today"
    todayBtn.addEventListener('click', (e) => {
        e.preventDefault();
        currentDate = new Date(); // Réinitialiser à la date actuelle
        renderCalendar(currentDate);
        
        let formatDate = formatDateString(currentDate);
        
        let TempM = formatDate.split("-")[1].replace(/^0/, '')

        let Y = formatDate.split("-")[0]
        let D = formatDate.split("-")[2].replace(/^0/, '')
        let M = parseInt(TempM)
                
        sidebarTitle.textContent = `${D} ${monthNames[M-1]}, ${Y}`;
        
        fetchReservations();
    });
    
    window.addEventListener('DOMContentLoaded', (event) => {
        const day = currentDate.getDate();
        const month = currentDate.getMonth();
        const year = currentDate.getFullYear();

        sidebarTitle.textContent = `${day} ${monthNames[month]}, ${year}`;
    });

    sidebarEventsList.innerHTML = '';
    login();
});
