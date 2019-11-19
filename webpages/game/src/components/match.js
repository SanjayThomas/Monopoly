import React from 'react';
import Table from 'react-bootstrap/Table';

export function Match(props) {
  let winners = [];
  let maxWins = -1;
  let playedGames = 0;

  for (let result of props.results) {
    if ('wins' in result) playedGames += result.wins;
    if (result.wins > maxWins) {
      maxWins = result.wins;
      winners = [result.name];
    }
    else if (result.wins === maxWins) { winners.append(result.name); }
  }


  return (
    <div>
      <h4 style={{ textDecoration: 'underline' }}>Match {props.id}</h4>
      <Table bordered>
        <thead>
          <tr className="list-group-item-dark">
            <th>Team Name</th>
            <th>Wins ({playedGames}/{props.totalGames})</th>
          </tr>
        </thead>
        <tbody>
          {props.results.map((result, index) => {
            return (
            <tr className={`${winners.includes(result.name) ? "list-group-item-success" : ""}`}>
              <td>{result.name}</td>
              <td>{'wins' in result ? result.wins : "Qualified by default"}</td>
            </tr>
            );
          })}
        </tbody>
      </Table>
    </div>
  );
}