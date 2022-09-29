const opn_data_class = {
  labels: opn_labels_class,
  datasets: [
    {
      label: 'Win',
      data: opn_win_data_class,
      backgroundColor: 'rgb(85,161,148)'
      
    },
    {
      label: 'Loss',
      data: opn_loss_data_class,
      backgroundColor: 'rgb(241,106,111)'
    
    },        
    {
      label: 'Draw',
      data: opn_draw_data_class,
      backgroundColor: 'rgb(152,160,166)'
    },
  ]
};

const opn_config_class = {
    type: 'bar',
    data: opn_data_class,
    options: {
      indexAxis: 'y',
      plugins: {
        title: {
          display: true,
          text: opn_title_class
        },
      },
      responsive: true,
      scales: {
        x: {
          stacked: true,
        },
        y: {
          stacked: true
        }
      }
    }
    };




const opnChartClass = new Chart(
    document.getElementById(opn_element_id_class),
    opn_config_class
    );