(function($) {
  'use strict';
  $(function() {
    if ($("#doughnutChartSales").length) { 
      const doughnutChartCrmCanvas = document.getElementById('doughnutChartSales');
      new Chart(doughnutChartCrmCanvas, {
        type: 'doughnut',
        data: {
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
          },
          responsive: true,
          maintainAspectRatio: false,
        }
      });
    }

    if ($("#salesTrendSales").length) { 
      const ctx = document.getElementById('salesTrendSales');
      var graphGradient = document.getElementById("salesTrendSales").getContext('2d');
      var graphGradient2 = document.getElementById("salesTrendSales").getContext('2d');
      var saleGradientBg = graphGradient.createLinearGradient(5, 0, 5, 100);
      saleGradientBg.addColorStop(0, 'rgba(42, 33, 186, 0.2)');
      saleGradientBg.addColorStop(1, 'rgba(42, 33, 186, 0)');
      var saleGradientBg2 = graphGradient2.createLinearGradient(100, 0, 50, 150);
      saleGradientBg2.addColorStop(0, 'rgba(0, 205, 255, 0.2)');
      saleGradientBg2.addColorStop(1, 'rgba(0, 205, 255, 0)');

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
              pointRadius: [0, 0, 0, 0, 0,0, 0, 0, 6, 0,0, 0, 0],
              pointHoverRadius: [0, 0, 0, 0, 0,0, 0, 0, 6, 0,0, 0, 0],
              pointBackgroundColor: ['','','','','','','','','#1F3BB3','','','','',''],
              pointBorderColor: ['','','','','','','','','#fff','','','','',''],
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
            pointRadius: [0, 0, 0, 0, 0,0, 0, 0, 0, 0,0, 0, 0],
            pointHoverRadius: [0, 0, 0, 0, 0,0, 0, 0, 0, 0,0, 0, 0],
            pointBackgroundColor: ['','','','','','','','','','','','','',''],
            pointBorderColor: ['','','','','','','','','','','','','',''],
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
    if ($("#salesReportSales").length) { 
      const leaveReportCanvas = document.getElementById('salesReportSales');
      new Chart(leaveReportCanvas, {
        type: 'bar',
        data: {
          labels: ["Jan","Feb", "Mar", "Apr", "May"],
          datasets: [{
            label: 'Last week',
            data: [350, 500, 100, 400, 550, 310, 240],
            backgroundColor: ["#F95F53", "#00CDFF", "#F95F53", "#00CDFF", "#00CDFF", "#F95F53", "#00CDFF"],
            borderColor: ["#F95F53", "#00CDFF", "#F95F53", "#00CDFF", "#00CDFF", "#F95F53", "#00CDFF"],
            borderWidth: 0,
            borderRadius: 40,
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
                display: true,
                drawBorder: false,
                color:"#F0F0F0",
                zeroLineColor: '#F0F0F0',
              },
              ticks: {
                beginAtZero: true,
                autoSkip: true,
                maxTicksLimit: 5,
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
                beginAtZero: false,
                autoSkip: true,
                maxTicksLimit: 7,
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

    if ($('#totalFollowers').length) {

      var bar = new ProgressBar.Circle(totalFollowers, {
        color: '#000',
        svgStyle: {
          strokeLinecap: 'round',
        },
        // This has to be the same size as the maximum width to
        // prevent clipping
        strokeWidth: 20,
        trailWidth: 20,
        easing: 'easeInOut',
        duration: 1400,
        text: { 
          autoStyleContainer: false
        },
        from: {
          color: '#203BB3',
          width: 20,
          radius: 100,
        },
        to: {
          color: '#203BB3',
          width: 20
        },
        // Set default step function for all animate calls
        step: function(state, circle) {
          circle.path.setAttribute('stroke', state.color);
          circle.path.setAttribute('stroke-width', state.width);
  
          var value = Math.round(circle.value() * 100);
          if (value === 0) {
            circle.setText('');
          } else {
            circle.setText(value);
          }
  
        }
      });
  
      bar.text.style.fontSize = '1.5rem';
      bar.text.style.fontWeight = 'bold';
      bar.animate(.80); // Number from 0.0 to 1.0
    }
    if ($('#totalCampaigns').length) {
      var bar = new ProgressBar.Circle(totalCampaigns, {
        color: '#000',
        svgStyle: {
          strokeLinecap: 'round',
        },
        // This has to be the same size as the maximum width to
        // prevent clipping
        strokeWidth: 20,
        trailWidth: 20,
        easing: 'easeInOut',
        duration: 1400,
        text: { 
          autoStyleContainer: false
        },
        from: {
          color: '#00CDFF',
          width: 20,
          radius: 100,
        },
        to: {
          color: '#00CDFF',
          width: 20
        },
        // Set default step function for all animate calls
        step: function(state, circle) {
          circle.path.setAttribute('stroke', state.color);
          circle.path.setAttribute('stroke-width', state.width);
  
          var value = Math.round(circle.value() * 100);
          if (value === 0) {
            circle.setText('');
          } else {
            circle.setText(value);
          }
  
        }
      });
  
      bar.text.style.fontSize = '1.5rem';
      bar.text.style.fontWeight = 'bold';
      bar.animate(.80); // Number from 0.0 to 1.0
    }
    
  });

  
})(jQuery);