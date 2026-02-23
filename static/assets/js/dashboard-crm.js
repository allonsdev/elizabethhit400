(function($) {
  'use strict';
  $(function() {

    if ($("#marketingOverviewCrm").length) { 
      const marketingOverviewCrmCanvas = document.getElementById('marketingOverviewCrm');
      new Chart(marketingOverviewCrmCanvas, {
        type: 'bar',
        data: {
          labels: ["Mon","Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
          datasets: [{
            label: 'Last week',
            data: [350, 500, 100, 400, 550, 310, 240],
            backgroundColor: "#2A21BA",
            borderColor: [
                '#2A21BA',
            ],
            borderWidth: 0,
            fill: true, // 3: no fill
            barPercentage: 0.5,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          elements: {
            line: {
                tension: 0.4,
            }
        },
        tooltips: {
            backgroundColor: 'rgba(31, 59, 179, 1)',
        },
          scales: {
            y: {
              border: {
                display: false
              },
              display: true,
              grid: {
                display: false,
              },
              ticks: {
                beginAtZero: true,
                autoSkip: true,
                maxTicksLimit: 6,
                fontSize: 10,
                color:"#6B778C", 
                font: {
                  size: 10,
                }
              }
            },
            x: {
              border: {
                display: false
              },
              display: true,
              grid: {
                display: false,
              },
              ticks: {
                beginAtZero: true,
                autoSkip: true,
                maxTicksLimit: 6,
                fontSize: 10,
                color:"#6B778C", 
                font: {
                  size: 10,
                }
              }
            }
          },
          plugins: {
            legend: {
                display: false,
            }
          }
        }
      });
    }

    if ($("#doughnutChartCrm").length) { 
      const doughnutChartCrmCanvas = document.getElementById('doughnutChartCrm');
      new Chart(doughnutChartCrmCanvas, {
        type: 'doughnut',
        data: {
          labels: [
            'Branch 1  ( 30% )',
            'Branch 2  ( 40% )',
            'Branch 3  ( 30% )'
          ],
          datasets: [{
            data: [40, 30, 30],
            backgroundColor: [
              "#1F3BB3",
              "#00CDFF",
              "#00AAB6"
            ],
            borderColor: [
              "#fff",
              "#fff",
              "#fff"
            ],
          }],
        },
        options: {
          cutout: 60,
          animationEasing: "easeOutBounce",
          animateRotate: true,
          animateScale: false,
          responsive: true,
          maintainAspectRatio: true,
          showScale: true,
          plugins: {
            legend: {
                display: false,
            }
          }
        },
        plugins: [{
          afterDatasetUpdate: function (chart, args, options) {
              const chartId = chart.canvas.id;
              var i;
              const legendId = `${chartId}-legend`;
              const ul = document.createElement('ul');
              for(i=0;i<chart.data.datasets[0].data.length; i++) {
                  ul.innerHTML += `
                  <li>
                    <span style="background-color: ${chart.data.datasets[0].backgroundColor[i]}"></span>
                    ${chart.data.labels[i]}
                  </li>
                `;
              }
              return document.getElementById(legendId).appendChild(ul);
            }
        }]
      });
    }

    if ($("#salesTrend").length) { 
      const ctx = document.getElementById('salesTrend');
      var graphGradient = document.getElementById("salesTrend").getContext('2d');
      var graphGradient2 = document.getElementById("salesTrend").getContext('2d');
      var saleGradientBg = graphGradient.createLinearGradient(5, 0, 5, 100);
      saleGradientBg.addColorStop(0, 'rgba(26, 115, 232, 0.18)');
      saleGradientBg.addColorStop(1, 'rgba(26, 115, 232, 0.02)');
      var saleGradientBg2 = graphGradient2.createLinearGradient(100, 0, 50, 150);
      saleGradientBg2.addColorStop(0, 'rgba(0, 208, 255, 0.19)');
      saleGradientBg2.addColorStop(1, 'rgba(0, 208, 255, 0.03)');

      new Chart(ctx, {
        type: 'line',
        data: {
          labels: ["SUN","sun", "MON", "mon", "TUE","tue", "WED", "wed", "THU", "thu", "FRI", "fri", "SAT"],
          datasets: [{
            label: 'Online Payment',
            data: [50, 110, 60, 290, 200, 115, 130, 170, 90, 210, 240, 280, 200],
            backgroundColor: saleGradientBg,
            borderColor: [
                '#2A21BA',
            ],
            borderWidth: 1.5,
            fill: true, // 3: no fill
            pointBorderWidth: 1,
            pointRadius: [4, 4, 4, 4, 4,4, 4, 4, 4, 4,4, 4, 4],
            pointHoverRadius: [2, 2, 2, 2, 2,2, 2, 2, 2, 2,2, 2, 2],
            pointBackgroundColor: ['#1F3BB3)', '#1F3BB3', '#1F3BB3', '#1F3BB3','#1F3BB3)', '#1F3BB3', '#1F3BB3', '#1F3BB3','#1F3BB3)', '#1F3BB3', '#1F3BB3', '#1F3BB3','#1F3BB3)'],
            pointBorderColor: ['#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff',],
        },{
          label: 'Offline Sales',
          data: [30, 150, 190, 250, 120, 150, 130, 20, 30, 15, 40, 95, 180],
          backgroundColor: saleGradientBg2,
          borderColor: [
              '#52CDFF',
          ],
          borderWidth: 1.5,
          fill: true, // 3: no fill
          pointBorderWidth: 1,
          pointRadius: [0, 0, 0, 4, 0],
          pointHoverRadius: [0, 0, 0, 2, 0],
          pointBackgroundColor: ['#00CDFF)', '#00CDFF', '#00CDFF', '#00CDFF','#00CDFF)', '#00CDFF', '#00CDFF', '#00CDFF','#00CDFF)', '#00CDFF', '#00CDFF', '#00CDFF','#00CDFF)'],
            pointBorderColor: ['#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff','#fff',],
      }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          elements: {
            line: {
                tension: 0.4,
            }
        },
        tooltips: {
            backgroundColor: 'rgba(31, 59, 179, 1)',
        },
        
          scales: {
            y: {
              border: {
                display: false
              },
              grid: {
                display: true,
                drawTicks: false,
                color:"#F0F0F0",
                zeroLineColor: '#F0F0F0',
              },
              ticks: {
                beginAtZero: false,
                autoSkip: true,
                maxTicksLimit: 4,
                color:"#6B778C",
                font: {
                  size: 10,
                }
              }
            },
            x: {
              border: {
                display: false
              },
              grid: {
                display: false,
                drawTicks: false,
              },
              ticks: {
                beginAtZero: false,
                autoSkip: true,
                maxTicksLimit: 7,
                color:"#6B778C",
                font: {
                  size: 10,
                }
              }
            }
          },
          plugins: {
            legend: {
                display: false,
            }
          }
        },
        plugins: [{
          afterDatasetUpdate: function (chart, args, options) {
              const chartId = chart.canvas.id;
              var i;
              const legendId = `${chartId}-legend`;
              const ul = document.createElement('ul');
              for(i=0;i<chart.data.datasets.length; i++) {
                  ul.innerHTML += `
                  <li>
                    <span style="background-color: ${chart.data.datasets[i].borderColor}"></span>
                    ${chart.data.datasets[i].label}
                  </li>
                `;
              }
              return document.getElementById(legendId).appendChild(ul);
            }
        }]
      });
    }

  });

  
})(jQuery);