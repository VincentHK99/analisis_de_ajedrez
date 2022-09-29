const opn_data_subclass = {
  labels: opn_labels_subclass,
  datasets: [
    {
      label: 'Win',
      data: opn_win_data_subclass,
      backgroundColor: 'rgb(85,161,148)'
      
    },
    {
      label: 'Loss',
      data: opn_loss_data_subclass,
      backgroundColor: 'rgb(241,106,111)'
    
    },        
    {
      label: 'Draw',
      data: opn_draw_data_subclass,
      backgroundColor: 'rgb(152,160,166)'
    },
  ]
};

const opn_config_subclass = {
    type: 'bar',
    data: opn_data_subclass,
    options: {
      indexAxis: 'y',
      plugins: {
        title: {
          display: true,
          text: opn_title_subclass
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




const opnChartSubclass = new Chart(
    document.getElementById(opn_element_id_subclass),
    opn_config_subclass
    );