const opn_data_eco = {
    labels: opn_labels_eco,
    datasets: [
      {
        label: 'Win',
        data: opn_win_data_eco,
        backgroundColor: 'rgb(85,161,148)'
        
      },
      {
        label: 'Loss',
        data: opn_loss_data_eco,
        backgroundColor: 'rgb(241,106,111)'
      
      },        
      {
        label: 'Draw',
        data: opn_draw_data_eco,
        backgroundColor: 'rgb(152,160,166)'
      },
    ]
  };

  const opn_config_eco = {
      type: 'bar',
      data: opn_data_eco,
      options: {
        indexAxis: 'y',
        plugins: {
          title: {
            display: true,
            text: opn_title_eco
          },
        },
        responsive: true,
        scales: {
          x: {
            stacked: true,
            max: 1
          },
          y: {
            stacked: true,
          }
        }
      }
      };




  const opnChartEco = new Chart(
      document.getElementById(opn_element_id_eco),
      opn_config_eco
      );