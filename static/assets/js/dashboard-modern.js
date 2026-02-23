(function($) {
  'use strict';
  $(function() {

    
    if ($("#modernRevenueGrowth").length) { 
      const ctx = document.getElementById('modernRevenueGrowth');
      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ["Jan","Feb", "Mar", "Apr", "May", "Jun", "Jul"],
          datasets: [{
            label: 'Last week',
            data: [50, 75, 100, 60, 70, 45, 90],
            backgroundColor: "#00CDFF",
            borderColor: [
                '#00CDFF',
            ],
            borderWidth: 0,
            fill: true, // 3: no fill
            barPercentage: 0.4,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          elements: {
            line: {
                tension: 0,
            },
            point:{
              radius: 0
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
              display:true,
              grid: {
                min: 1,
                display: true,
                drawTicks: false,
                color:"#F0F0F0",
                zeroLineColor: '#F0F0F0',
                drawBorder: false
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
              display:true,
              grid: {
                display: false,
                drawTicks: false,
                drawBorder: false
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
        }
      });
    }

    if ($("#modernBubble").length) { 
      const ctx = document.getElementById('modernBubble');
      new Chart(ctx, {
        type: 'bubble',
        data: {
          labels: ["Jan","Feb", "Mar", "Apr", "May", "Jun", "Jul"],
        datasets: [{
          label: 'Money send',
          data: [{
            x: 10,
            y: 100,
            r: 10
          }, {
            x: 20,
            y: 500,
            r: 15
          }, {
            x: 40,
            y: 100,
            r: 10
          }, {
            x: 55,
            y: 200,
            r: 10
          }, {
            x: 70,
            y: 500,
            r: 10
          }, {
            x: 0,
            y: 600,
            r: 0
          }],
          backgroundColor: 'rgb(30,59,179)'
        },{
          label: 'Money Received',
          data: [{
            x: 10,
            y: 300,
            r: 5
          }, {
            x: 30,
            y: 400,
            r: 5
          }, {
            x: 60,
            y: 410,
            r: 10
          }, {
            x: 100,
            y: 370,
            r: 5
          }, {
            x: 110,
            y: 0,
            r: 0
          }],
          backgroundColor: 'rgb(99,171,253)',
        }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          elements: {
            line: {
                tension: 0,
            },
            point:{
              radius: 0
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
              display:true,
              grid: {
                min: 1,
                display: true,
                drawTicks: false,
                color:"#F0F0F0",
                zeroLineColor: '#F0F0F0',
                drawBorder: false
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
              display:true,
              grid: {
                display: false,
                drawTicks: false,
                drawBorder: false
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
                    <span style="background-color: ${chart.data.datasets[i].backgroundColor}"></span>
                    ${chart.data.datasets[i].label}
                  </li>
                `;
              }
              return document.getElementById(legendId).appendChild(ul);
            }
        }]
      });
    }


    if ($("#moneyFlow").length) { 
      const ctx = document.getElementById('moneyFlow');
      var graphGradient = document.getElementById("moneyFlow").getContext('2d');
      var moneyFlowGradientBg = graphGradient.createLinearGradient(10, 10, 1, 160);
      moneyFlowGradientBg.addColorStop(1, 'rgba(30, 59, 179, 0)');
      moneyFlowGradientBg.addColorStop(0, 'rgba(30, 59, 179, 0.3)');

      new Chart(ctx, {
        type: 'line',
        data: {
          labels: ["jan","feb", "mar", "apr", "may", "jun", "july", "aug", "sep", "oct", "nov", "dec"],
          datasets: [{
            label: 'Last week',
            data: [20000, 50000, 30000, 80000, 60000, 55000, 45000, 60000, 35000, 50000, 55000, 40000],
            backgroundColor: moneyFlowGradientBg,
            borderWidth: 2,
            pointBorderWidth:0,
            borderColor: [
                '#1E3BB3',
            ],
            fill: true, // 3: no fill   
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
                drawBorder: false
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
                drawBorder: false
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
      });
    }


    if ($("#modernChartliability").length) { 
      const doughnutChartCrmCanvas = document.getElementById('modernChartliability');
      new Chart(doughnutChartCrmCanvas, {
        type: 'doughnut',
        data: {
          datasets: [{
            data: [50, 20, 30],
            backgroundColor: [
              "#4DA761",
              "#00CDFF",
              "#EE5E51",
            ],
            borderColor: [
              "#fff",
              "#fff",
              "#fff",
            ],
          }],
    
          // These labels appear in the legend and in the tooltips when hovering different arcs
          labels: [
            'Current',
            'New',
            'Pending',
          ]
        },
        options: {
          cutout: 40,
          animationEasing: "easeOutBounce",
          animateRotate: true,
          animateScale: false,
          showScale: true,
          plugins: {
            legend: {
                display: false,
            }
          },
          responsive: true,
          maintainAspectRatio: true,
          tooltips: {
            backgroundColor: '#fff',
            titleFontSize: 14,
            titleFontColor: '#0B0F32',
            bodyFontColor: '#737F8B',
            bodyFontSize: 11,
            displayColors: false
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
  });

  
})(jQuery);