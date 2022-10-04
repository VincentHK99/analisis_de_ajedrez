
const data = {
    labels: labels,
    datasets: [
      {
        label: 'Win',
        data: win_data,
        backgroundColor: 'rgb(85,161,148)'
        
      },
      {
        label: 'Loss',
        data: loss_data,
        backgroundColor: 'rgb(241,106,111)'
      
      },        
      {
        label: 'Draw',
        data: draw_data,
        backgroundColor: 'rgb(152,160,166)'
      },
    ]
  };
  let delayed;
  const config = {
      type: 'bar',
      data: data,
      options: {
        indexAxis: 'y',
        plugins: {
          title: {
            display: true,
            text: title
          },
        },
        responsive: true,
        scales: {
          x: {
            stacked: true,
            max: 1
          },
          y: {
            stacked: true
          }
        }
      }
      };




  const myChart = new Chart(
      document.getElementById(element_id),
      config
      );