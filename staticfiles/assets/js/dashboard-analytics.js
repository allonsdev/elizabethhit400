(function($) {
  'use strict';
  $(function() {
    if ($("#doughnutChartAnalytic").length) { 
      const doughnutChartCrmCanvas = document.getElementById('doughnutChartAnalytic');
      new Chart(doughnutChartCrmCanvas, {
        type: 'doughnut',
        data: {
          datasets: [{
            data: [50, 20, 30],
            backgroundColor: [
              "#1F3BB3",
              "#00CDFF",
              "#F95F53",
            ],
            borderColor: [
              "#fff",
              "#fff",
              "#fff",
            ],
          }],
    
          // These labels appear in the legend and in the tooltips when hovering different arcs
          labels: [
            'Admin dashboard',
            'Website design',
            'Mobile app design',
          ]
        },
        options: {
          cutout: 50,
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
                    <span class="data-value">${chart.data.datasets[0].data[i]}%</span> 
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

    if ($("#realTimeUserAnalytic").length) { 
      const ctx = document.getElementById('realTimeUserAnalytic');
      var realTimegradient = document.getElementById("realTimeUserAnalytic").getContext('2d');
      var realTimegradient = realTimegradient.createLinearGradient(1, 0, 1, 70);
      realTimegradient.addColorStop(1, 'rgba(30, 59, 179, 0.1)');
      realTimegradient.addColorStop(0, 'rgba(30, 59, 179, 0.8)');
      new Chart(ctx, {
        type: 'line',
        data: {
          labels: ["jan","feb", "mar", "apr", "may", "jun", "july", "aug", "sep", "oct"],
        datasets: [{
          label: 'Last week',
          data: [0, 10, 9, 16, 15, 17, 16, 18, 14, 25],
          backgroundColor: realTimegradient,
          borderWidth: 1.5,
          pointBorderWidth:0,
          borderColor: [
              '#1E3BB3',
          ],
          fill: true, // 3: no fill  
          pointRadius: 0,
        }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          elements: {
            line: {
                tension: .4,
            }
          },
          scales: {
            x: {
              border: {
                display: false
              },
              grid: {
                display: false,
                drawTicks: true,
              },
              ticks: {
                color: "#6C7383",
                display:false,
                beginAtZero: false,
                steps: 100,
                stepValue: 5,
                max: 150
              },
            },
            y: {
              beginAtZero: true,
              border: {
                display: false
              },
              grid: {
                display:false,
              },
              ticks: {
                color: "#6C7383",
                beginAtZero: false,
                stepsize:10,
                display:false,
              },
            }
          },
          plugins: {
            legend: {
                display: false,
                labels: {
                    color: 'rgb(255, 99, 132)'
                }
            }
          }
        },
      });
    }

    if ($("#totalEarningsAnalytic").length) { 
      const ctx = document.getElementById('totalEarningsAnalytic');
      var totalEarningsgradient = document.getElementById("totalEarningsAnalytic").getContext('2d');
      var totalEarningsgradient = totalEarningsgradient.createLinearGradient(1, 0, 1, 70);
      totalEarningsgradient.addColorStop(1, 'rgba(0, 170, 183, 0.1)');
      totalEarningsgradient.addColorStop(0, 'rgba(0, 170, 183, 0.8)');
      new Chart(ctx, {
        type: 'line',
        data: {
          labels: ["jan","feb", "mar", "apr", "may", "jun", "july", "aug", "sep", "oct"],
        datasets: [{
          label: 'Last week',
          data: [0, 10, 9, 16, 15, 17, 16, 18, 14, 25],
          backgroundColor: totalEarningsgradient,
          borderWidth: 1.5,
          pointBorderWidth:0,
          borderColor: [
              '#00AAB7',
          ],
          fill: true, // 3: no fill   
          pointRadius: 0,
        }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          elements: {
            line: {
                tension: .4,
            }
          },
          scales: {
            x: {
              border: {
                display: false
              },
              grid: {
                display: false,
                drawTicks: true,
              },
              ticks: {
                color: "#6C7383",
                display:false,
                beginAtZero: false,
                steps: 100,
                stepValue: 5,
                max: 150
              },
            },
            y: {
              beginAtZero: true,
              border: {
                display: false
              },
              grid: {
                display:false,
              },
              ticks: {
                color: "#6C7383",
                beginAtZero: false,
                stepsize:10,
                display:false,
              },
            }
          },
          plugins: {
            legend: {
                display: false,
                labels: {
                    color: 'rgb(255, 99, 132)'
                }
            }
          }
        },
      });
    }

    if ($("#impressionAnalytic").length) { 
      const ctx = document.getElementById('impressionAnalytic');
      var impressionAnalyticgradient = document.getElementById("impressionAnalytic").getContext('2d');
      var impressionAnalyticgradient = impressionAnalyticgradient.createLinearGradient(1, 0, 1, 70);
      impressionAnalyticgradient.addColorStop(1, 'rgba(77, 167, 97, 0.1)');
      impressionAnalyticgradient.addColorStop(0, 'rgba(77, 167, 97, 0.8)');
      new Chart(ctx, {
        type: 'line',
        data: {
          labels: ["jan","feb", "mar", "apr", "may", "jun", "july", "aug", "sep", "oct"],
          datasets: [{
            label: 'Last week',
            data: [0, 10, 9, 16, 15, 17, 16, 18, 14, 25],
            backgroundColor: impressionAnalyticgradient,
            borderWidth: 1.5,
            pointBorderWidth:0,
            borderColor: [
                '#4DA761',
            ],
            fill: true, // 3: no fill   
            pointRadius:0,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          elements: {
            line: {
                tension: .4,
            }
          },
          scales: {
            x: {
              border: {
                display: false
              },
              grid: {
                display: false,
                drawTicks: true,
              },
              ticks: {
                color: "#6C7383",
                display:false,
                beginAtZero: false,
                steps: 100,
                stepValue: 5,
                max: 150
              },
            },
            y: {
              beginAtZero: true,
              border: {
                display: false
              },
              grid: {
                display:false,
              },
              ticks: {
                color: "#6C7383",
                beginAtZero: false,
                stepsize:10,
                display:false,
              },
            }
          },
          plugins: {
            legend: {
                display: false,
                labels: {
                    color: 'rgb(255, 99, 132)'
                }
            }
          }
        },
      });
    }


    if ($("#realtimestatisticsAnalytic").length) { 
      const realtimestatisticsAnalyticCanvas = document.getElementById('realtimestatisticsAnalytic');
      new Chart(realtimestatisticsAnalyticCanvas, {
        type: 'bar',
        data: {
          labels: ["Jan","Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        datasets: [{
          label: 'Last week',
          data: [125, 169, 60, 140, 100, 170, 50, 80, 240, 140, 80, 160],
          backgroundColor: "#1E3BB3",
          borderColor: [
              '#1E3BB3',
          ],
          borderWidth: 0,
          fill: true, // 3: no fill
          barPercentage: 0.8,
        },
        {
          label: 'Last week',
          
          data: [200, 290, 220, 180, 200, 250, 120, 170, 290, 210, 170, 210],
          backgroundColor: "#E3E9FF",
          borderColor: [
              '#E3E9FF',
          ],
          borderWidth: 0,
          fill: true, // 3: no fill
          barPercentage: 0.8,
        }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          elements: {
            line: {
                tension: .4,
            }
          },
          scales: {
            x: {

              stacked:true,
              border: {
                display: false
              },
              grid: {
                display: false,
                drawTicks: true,
              },
              ticks: {
                color: "#6C7383",
                display:true,
                beginAtZero: false,
                steps: 100,
                stepValue: 5,
                max: 150
              },
            },
            y: {

              stacked:true,
              beginAtZero: true,
              border: {
                display: false
              },
              grid: {
                display:true,
              },
              ticks: {
                color: "#6C7383",
                beginAtZero: false,
                stepsize:10,
                display:true,
              },
            }
          },
          plugins: {
            legend: {
                display: false,
                labels: {
                    color: 'rgb(255, 99, 132)'
                }
            }
          }
        },
      });
    }

    if ($('#totalVisitorsanalytic').length) {
      var bar = new ProgressBar.Circle(totalVisitorsanalytic, {
        color: '#fff',
        // This has to be the same size as the maximum width to
        // prevent clipping
        strokeWidth: 15,
        trailWidth: 15, 
        easing: 'easeInOut',
        duration: 1400,
        text: {
          autoStyleContainer: false
        },
        from: {
          color: '#00CDFF',
          width: 15
        },
        to: {
          color: '#00CDFF',
          width: 15
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
  
      bar.text.style.fontSize = '0rem';
      bar.animate(.64); // Number from 0.0 to 1.0
    }
    if ($('#visitperdayAnalytic').length) {
      var bar = new ProgressBar.Circle(visitperdayAnalytic, {
        color: '#fff',
        // This has to be the same size as the maximum width to
        // prevent clipping
        strokeWidth: 15,
        trailWidth: 15,
        easing: 'easeInOut',
        duration: 1400,
        text: {
          autoStyleContainer: false
        },
        from: {
          color: '#1E3BB3',
          width: 15
        },
        to: {
          color: '#1E3BB3',
          width: 15
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
  
      bar.text.style.fontSize = '0rem';
      bar.animate(.34); // Number from 0.0 to 1.0
    }
    
    if ($("#performanceAnalytic").length) { 
      const ctx = document.getElementById('performanceAnalytic');
      var performanceAnalyticgradient = document.getElementById("performanceAnalytic").getContext('2d');
      var performanceAnalyticgradient = performanceAnalyticgradient.createLinearGradient(10, 10, 1, 160);
      performanceAnalyticgradient.addColorStop(1, 'rgba(0, 170, 183, 0)');
      performanceAnalyticgradient.addColorStop(0, 'rgba(0, 170, 183, 0.6)');
      new Chart(ctx, {
        type: 'line',
        data: {
          labels: ["one","two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen"],
          datasets: [{
            label: 'Last week',
            data: [30, 20, 25, 22, 35, 18, 22, 20, 34, 17, 24, 22, 36],
            borderWidth: 1,
            pointBorderWidth:0,
            borderColor: [
                '#00AAB7',
            ],
            fill: false, // 3: no fill   
          },
          {
            label: 'Last week',
            data: [28, 18, 23, 20, 33, 16, 20, 18, 32, 15, 22, 20, 34],
            backgroundColor: performanceAnalyticgradient,
            borderWidth: 0,
            pointBorderWidth:0,
            fill: true, // 3: no fill   
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
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
              display:false,
              grid: {
                display: false,
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
              display:false,
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
        }
      });
    }
    
  });

  if ($("#siteIncomeAnalytic").length) { 
    const ctx = document.getElementById('siteIncomeAnalytic');
    var siteIncomeAnalyticgradient = document.getElementById("siteIncomeAnalytic").getContext('2d');
    var siteIncomeAnalyticgradient = siteIncomeAnalyticgradient.createLinearGradient(1, 0, 1, 70);
    siteIncomeAnalyticgradient.addColorStop(1, 'rgba(245, 99, 83, 0.1)');
    siteIncomeAnalyticgradient.addColorStop(0, 'rgba(245, 99, 83, 0.8)');
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: ["jan","feb", "mar", "apr", "may", "jun", "july", "aug", "sep", "oct"],
        datasets: [{
          label: 'Last week',
          data: [0, 10, 9, 16, 15, 17, 16, 18, 14, 25],
          backgroundColor: siteIncomeAnalyticgradient,
          borderWidth: 1.5,
          pointBorderWidth:0,
          borderColor: [
              '#f5422f',
          ],
          fill: true, // 3: no fill 
          pointRadius:0,  
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        elements: {
          line: {
              tension: .4,
          }
        },
        scales: {
          x: {
            border: {
              display: false
            },
            grid: {
              display: false,
              drawTicks: true,
            },
            ticks: {
              color: "#6C7383",
              display:false,
              beginAtZero: false,
              steps: 100,
              stepValue: 5,
              max: 150
            },
          },
          y: {
            beginAtZero: true,
            border: {
              display: false
            },
            grid: {
              display:false,
            },
            ticks: {
              color: "#6C7383",
              beginAtZero: false,
              stepsize:10,
              display:false,
            },
          }
        },
        plugins: {
          legend: {
              display: false,
              labels: {
                  color: 'rgb(255, 99, 132)'
              }
          }
        }
      },
    });
  }

  
})(jQuery);