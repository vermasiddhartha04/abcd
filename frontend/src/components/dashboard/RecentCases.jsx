function RecentCases() {
  return (
    <div className="recent-cases">
      <h2>Recent Cases</h2>

      <table>
        <thead>
          <tr>
            <th>Case</th>
            <th>GSTIN</th>
            <th>Status</th>
          </tr>
        </thead>

        <tbody>
          <tr>
            <td>ABC Pvt Ltd</td>
            <td>05ABCDE1234F1Z5</td>
            <td>Pending</td>
          </tr>

          <tr>
            <td>XYZ Traders</td>
            <td>07XYZAB1234K1Z8</td>
            <td>Completed</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}

export default RecentCases;