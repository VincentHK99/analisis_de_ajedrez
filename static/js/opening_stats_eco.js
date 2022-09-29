const opn_data = {
    labels: opn_labels,
    datasets: [
      {
        label: 'Win',
        data: opn_win_data,
        backgroundColor: 'rgb(85,161,148)'
        
      },
      {
        label: 'Loss',
        data: opn_loss_data,
        backgroundColor: 'rgb(241,106,111)'
      
      },        
      {
        label: 'Draw',
        data: opn_draw_data,
        backgroundColor: 'rgb(152,160,166)'
      },
    ]
  };

  const opn_config = {
      type: 'bar',
      data: opn_data,
      options: {
        indexAxis: 'y',
        plugins: {
          title: {
            display: true,
            text: opn_title
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




  const opnChart = new Chart(
      document.getElementById(opn_element_id),
      opn_config
      );