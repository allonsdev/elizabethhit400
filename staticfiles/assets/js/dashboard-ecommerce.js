(function($) {
  'use strict';
  $(function() {



    if ($("#summarySales").length) { 
      const ctx = document.getElementById('summarySales');
      var graphGradient = document.getElementById("summarySales").getContext('2d');
      var summarySalesGradientBg = graphGradient.createLinearGradient(10, 10, 1, 160);
      summarySalesGradientBg.addColorStop(1, 'rgba(30, 59, 179, 0)');
      summarySalesGradientBg.addColorStop(0, 'rgba(30, 59, 179, 0.3)');
      var pointBg = ["rgba(255,255,255,0)","rgba(255,255,255,0)","rgba(255,255,255,0)","rgba(255,255,255,0)","rgba(255,255,255,0)","rgba(255,255,255,0)","#1E3BB3","rgba(255,255,255,0)","rgba(255,255,255,0)","rgba(255,255,255,0)","rgba(255,255,255,0)","rgba(255,255,255,0)"];
      var pointBorder = ["rgba(255,255,255,0)","rgba(255,255,255,0)","rgba(255,255,255,0)","rgba(255,255,255,0)","rgba(255,255,255,0)","rgba(255,255,255,0)","#fff","rgba(255,255,255,0)","rgba(255,255,255,0)","rgba(255,255,255,0)","rgba(255,255,255,0)","rgba(255,255,255,0)"];
      new Chart(ctx, {
        type: 'line',
        data: {
          labels: ["jan","feb", "mar", "apr", "may", "jun", "july", "aug", "sep", "oct", "nov", "dec"],
          datasets: [{
            label: 'Last week',
            data: [20000, 50000, 30000, 80000, 60000, 55000, 45000, 60000, 35000, 50000, 55000, 40000],
            backgroundColor: summarySalesGradientBg,
            borderWidth: 2,
            borderColor: [
                '#1E3BB3',
            ],
            fill: true, // 3: no fill  
            
            pointBackgroundColor:  pointBg,
            pointBorderColor: pointBorder,
            radius: 5,
            pointRadius: 5
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


    if ($("#customerOverviewEcommerce").length) { 
      const customerOverviewEcommerceCanvas = document.getElementById('customerOverviewEcommerce');
      new Chart(customerOverviewEcommerceCanvas, {
        type: 'doughnut',
        data: {
          datasets: [{
            data: [50, 20, 30],
            backgroundColor: [
              "#1E3BB3",
              "#00CDFF",
              "#00AAB7",
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
            'Retargeted',
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

    if ($("#totalSalesByUnit").length) { 
      const totalSalesByUnitCanvas = document.getElementById('totalSalesByUnit');
      new Chart(totalSalesByUnitCanvas, {
        type: 'pie',
        data: {
          datasets: [{
            data: [20, 55, 25],
            backgroundColor: [
              "#4DA761",
              "#F95F53",
              "#00CDFF",
            ],
            borderColor: [
              "#4DA761",
              "#F95F53",
              "#00CDFF",
            ],
          }],
    
          // These labels appear in the legend and in the tooltips when hovering different arcs
          labels: [
            'Online',
            'Offline',
            'Marketing',
          ]
        },
        options: {
          cutout: 0,
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

    if ($("#incomeExpences").length) { 
      const ctx = document.getElementById('incomeExpences');
      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ["Jan","Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
          datasets: [{
            label: 'Income',
            data: [125, 169, 60, 140, 100, 170, 50, 80, 240, 140, 80, 160],
            backgroundColor: "#1E3BB3",
            borderColor: [
                '#1E3BB3',
            ],
            borderWidth: 0,
            fill: true, // 3: no fill
            barPercentage: 0.4,
              
          },
          {
            label: 'Expense',
            
            data: [200, 290, 220, 180, 200, 250, 120, 170, 290, 210, 170, 210],
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
              stacked: true,
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
              stacked: true,
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

    if ($('#carouselExampleControls').length) {
      var myCarousel = document.querySelector('#carouselExampleControls')
      var carousel = new bootstrap.Carousel(myCarousel)
    }
  });
})(jQuery);